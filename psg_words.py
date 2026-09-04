"""Symbolic PSG words (PLAN.md node N3): one ASCII word per 30 s epoch, per-night quantile bins.

Word layout, 11 space-separated fields, fixed positions (a<b<c<d = night quartiles, ? = missing):
  D T A S B   6 letters each: relative delta/theta/alpha/sigma/beta power per 5 s window
  w           slow-wave fraction of epoch (AASM 75 uV, 0.5-2 Hz): 0 / 1 (<20%) / 2 (20-50%) / 3 (>50%)
  p           yasa spindle count bucket 0/1/2/3+
  E           3 chars: REM-count bucket 0-3, SEM slow-power quartile a-d, L/R phase x(out)/i(in)/n
  M           6 letters: chin EMG log-RMS (10-45 Hz) per 5 s window, night quartiles
  O           3 chars: SpO2 min quartile, mean quartile, desat>=3% flag 0/1
  h           hours since recording start, single digit 0-9 (ponytail: lights-off proxy; MESA has no LIGHT channel)
CLI: python psg_words.py --nights DIR --out DIR      (jsonl per night: id cohort epoch stage word)
     python psg_words.py --selfcheck [--nights DIR]   (token budget, stage vocab, LONO LR gate)
"""
import argparse, glob, json, os, sys, warnings
import numpy as np
from scipy.signal import butter, sosfiltfilt, welch

EPOCH, WIN = 30, 5
BANDS = [(0.5, 4), (4, 8), (8, 12), (12, 16), (16, 30)]
STAGE_LETTER = "WABCR"  # W N1 N2 N3 R
Q = (25, 50, 75)


def qbin(x, cuts=None):
    """Per-night quartile letters a-d; NaN -> '?'. cuts lets callers share breakpoints."""
    x = np.asarray(x, float)
    if cuts is None:
        cuts = np.nanpercentile(x, Q) if np.isfinite(x).any() else np.zeros(3)
    idx = np.searchsorted(cuts, x, side="right")
    return np.where(np.isfinite(x), np.array(list("abcd"))[np.clip(idx, 0, 3)], "?")


def bandpass(x, lo, hi, fs, order=4):
    sos = butter(order, [lo, min(hi, 0.45 * fs)], btype="band", fs=fs, output="sos")
    return sosfiltfilt(sos, x)


def artifact_windows(eeg, fs, rail):
    """Per 5 s window: True if saturated (>=2% samples at ADC rail) or flat (std < 0.5 uV)."""
    w = eeg.reshape(-1, WIN * fs)
    return ((np.abs(w) >= 0.98 * rail).mean(1) >= 0.02) | (w.std(1) < 0.5)


def eeg_bandpowers(eeg, fs, bad):
    """-> (n_epoch, 6 win, 5 band) relative power; NaN on artifact windows."""
    w = eeg.reshape(-1, WIN * fs)
    f, p = welch(w, fs=fs, nperseg=2 * fs, axis=-1)
    tot = p[:, (f >= 0.5) & (f <= 30)].sum(-1)
    rel = np.stack([p[:, (f >= lo) & (f < hi)].sum(-1) for lo, hi in BANDS], -1) / np.maximum(tot, 1e-12)[:, None]
    rel[bad] = np.nan
    return rel.reshape(-1, EPOCH // WIN, len(BANDS))


def slow_wave_fraction(eeg, fs, bad_epoch):
    """Fraction of each epoch covered by half-waves (0.5-2 Hz) with p2p > 75 uV; NaN on artifact epochs."""
    x = bandpass(eeg, 0.3, 2.0, fs)
    zc = np.flatnonzero(np.diff(np.signbit(x)))
    cover = np.zeros(len(x), bool)
    for a, b in zip(zc[:-2], zc[2:]):  # full wave = two half-waves
        seg = x[a:b]
        if 0.5 * fs <= b - a <= 2.0 * fs and seg.max() - seg.min() > 75:
            cover[a:b] = True
    out = cover.reshape(-1, EPOCH * fs).mean(1)
    out[bad_epoch] = np.nan
    return out


def spindle_counts(eeg, fs, n_epoch, bad_epoch):
    """yasa detector on the whole night (no hypnogram: that would leak labels), zeroed on artifact epochs."""
    try:
        import yasa
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sp = yasa.spindles_detect(eeg, fs, thresh={"rel_pow": 0.15, "corr": 0.6, "rms": 1.2}, verbose=False)
        c = np.zeros(n_epoch, int) if sp is None else \
            np.bincount((sp.summary()["Peak"].values // EPOCH).astype(int), minlength=n_epoch)[:n_epoch]
    except Exception as e:  # yasa missing or failed: sigma-burst fallback, logged
        print(f"  spindles: yasa failed ({e}); sigma-burst fallback", file=sys.stderr)
        env = np.abs(bandpass(eeg, 12, 15, fs)).reshape(n_epoch, -1)
        thr = np.percentile(env, 95)
        c = (np.diff((env > thr).astype(int), axis=1) == 1).sum(1)
    c[bad_epoch] = 0
    return c


def eog_feats(l, r, fs, n_epoch):
    """-> rem count per epoch, SEM slow power per epoch, L/R phase corr per epoch."""
    d = bandpass(l - r, 0.5, 5, fs).reshape(n_epoch, -1)  # difference cancels in-phase EEG bleed
    thr = np.percentile(np.abs(d), 97)
    rem = ((np.abs(d) > thr)[:, 1:] & ~(np.abs(d) > thr)[:, :-1]).sum(1)  # threshold crossings
    slow = np.log(bandpass(l - r, 0.15, 0.6, fs).reshape(n_epoch, -1).var(1) + 1e-9)
    lf, rf = bandpass(l, 0.3, 5, fs).reshape(n_epoch, -1), bandpass(r, 0.3, 5, fs).reshape(n_epoch, -1)
    lf, rf = lf - lf.mean(1, keepdims=True), rf - rf.mean(1, keepdims=True)
    corr = (lf * rf).sum(1) / np.maximum(np.sqrt((lf ** 2).sum(1) * (rf ** 2).sum(1)), 1e-9)
    return rem, slow, corr


def night_to_words(night):
    st = np.asarray(night["stages"]); n = len(st)
    fs_eeg, fs_eog, fs_emg = int(night["fs_eeg"]), int(night["fs_eog"]), int(night["fs_emg"])
    rail = float(night["rail"]) if "rail" in night else np.inf
    eeg = np.asarray(night["eeg"], float)[: n * EPOCH * fs_eeg]
    bad = artifact_windows(eeg, fs_eeg, rail)
    bad_epoch = bad.reshape(n, -1).mean(1) > 0.5
    # EEG bands: quartiles per band over all clean 5 s windows of the night
    rel = eeg_bandpowers(eeg, fs_eeg, bad)
    bands = [qbin(rel[:, :, b].ravel()).reshape(n, -1) for b in range(len(BANDS))]
    swf = slow_wave_fraction(eeg, fs_eeg, bad_epoch)
    sw = np.where(np.isfinite(swf), np.digitize(np.nan_to_num(swf), [1e-9, 0.2, 0.5]).astype(str), "?")
    sp = np.minimum(spindle_counts(eeg, fs_eeg, n, bad_epoch), 3)
    rem, slow, corr = eog_feats(np.asarray(night["eog_l"], float)[: n * EPOCH * fs_eog],
                                np.asarray(night["eog_r"], float)[: n * EPOCH * fs_eog], fs_eog, n)
    remb = np.digitize(rem, [1, 4, 10]); semq = qbin(slow)
    phase = np.where(corr < -0.1, "x", np.where(corr > 0.45, "i", "n"))
    emg = bandpass(np.asarray(night["emg"], float)[: n * EPOCH * fs_emg], 10, 45, fs_emg)
    rms = np.log(np.sqrt((emg.reshape(-1, WIN * fs_emg) ** 2).mean(1)) + 1e-6)
    emgq = qbin(rms).reshape(n, -1)
    spo2 = np.asarray(night["spo2"], float)[: n * EPOCH].reshape(n, EPOCH)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        smin, smean, smax = np.nanmin(spo2, 1), np.nanmean(spo2, 1), np.nanmax(spo2, 1)
    prev_max = np.r_[smax[:1], smax[:-1]]
    desat = np.where(np.isfinite(smin), (np.fmax(smax, prev_max) - smin >= 3).astype(int).astype(str), "?")
    hour = np.minimum(np.arange(n) * EPOCH // 3600, 9)
    smin_q, smean_q = qbin(smin), qbin(smean)
    words = []
    for i in range(n):
        f = ["".join(b[i]) for b in bands] + [sw[i], str(sp[i]), f"{remb[i]}{semq[i]}{phase[i]}",
             "".join(emgq[i]), f"{smin_q[i]}{smean_q[i]}{desat[i]}", str(hour[i])]
        words.append(" ".join(f))
    return words


def load_words(nights_dir):
    """-> list of dict(id, cohort, epoch, stage, word) over all npz in dir, unscored epochs dropped."""
    rows = []
    for p in sorted(glob.glob(os.path.join(nights_dir, "*.npz"))):
        nt = np.load(p)
        w = night_to_words(nt)
        st = nt["stages"]
        rows += [{"id": str(nt["id"]), "cohort": str(nt["cohort"]), "epoch": i, "stage": STAGE_LETTER[s], "word": w[i]}
                 for i, s in enumerate(st) if s >= 0]
    return rows


def selfcheck(nights_dir):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score
    from transformers import AutoTokenizer
    rows = load_words(nights_dir)
    assert rows, f"no nights in {nights_dir}"
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    lens = [len(tok(r["word"])["input_ids"]) for r in rows]
    print(f"epochs={len(rows)} nights={len({r['id'] for r in rows})} tokens/epoch max={max(lens)} mean={np.mean(lens):.1f}")
    assert max(lens) <= 40, "token budget exceeded"
    for s in STAGE_LETTER:
        assert len(tok(s)["input_ids"]) == 1, f"stage {s} not a single token"
    present = {r["stage"] for r in rows}
    assert present == set(STAGE_LETTER), f"stages missing from dev nights: {set(STAGE_LETTER) - present}"
    for s in STAGE_LETTER:
        ex = [r["word"] for r in rows if r["stage"] == s][:5]
        print(f"  {s}: " + " | ".join(ex[:2]))
    # positional char features: token = field index + char position + char
    def feats(w):
        return " ".join(f"{fi}{ci}{c}" for fi, fld in enumerate(w.split()) for ci, c in enumerate(fld))
    vec = CountVectorizer(token_pattern=r"\S+", binary=True).fit([feats(r["word"]) for r in rows])
    ids = sorted({r["id"] for r in rows}); f1s = []
    for held in ids:
        tr = [r for r in rows if r["id"] != held]; te = [r for r in rows if r["id"] == held]
        clf = LogisticRegression(max_iter=2000, C=0.5, class_weight="balanced")
        clf.fit(vec.transform([feats(r["word"]) for r in tr]), [r["stage"] for r in tr])
        pred = clf.predict(vec.transform([feats(r["word"]) for r in te]))
        f1 = f1_score([r["stage"] for r in te], pred, average="macro", labels=list(STAGE_LETTER), zero_division=0)
        per = f1_score([r["stage"] for r in te], pred, average=None, labels=list(STAGE_LETTER), zero_division=0)
        f1s.append(f1); print(f"  LONO {held}: macroF1={f1:.3f} per-class W/N1/N2/N3/R={np.round(per, 2).tolist()}")
    print(f"GATE LR-on-words LONO macro-F1 mean={np.mean(f1s):.3f} min={min(f1s):.3f}")
    assert np.mean(f1s) > 0.5, "GATE FAILED: tokenizer carries too little signal"
    print("selfcheck OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nights", default="/tmp/nsrr-dev/nights"); ap.add_argument("--out")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        selfcheck(a.nights); sys.exit(0)
    os.makedirs(a.out, exist_ok=True)
    for p in sorted(glob.glob(os.path.join(a.nights, "*.npz"))):
        nt = np.load(p); w = night_to_words(nt)
        with open(os.path.join(a.out, str(nt["id"]) + ".jsonl"), "w") as f:
            for i, s in enumerate(nt["stages"]):
                if s >= 0:
                    f.write(json.dumps({"id": str(nt["id"]), "cohort": str(nt["cohort"]), "epoch": i,
                                        "stage": STAGE_LETTER[s], "word": w[i]}) + "\n")
        print(f"{nt['id']}: {len(w)} words -> {a.out}")
