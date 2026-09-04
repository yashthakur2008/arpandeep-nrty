"""NSRR loader (PLAN.md node N1): EDF + NSRR XML -> per-night npz.

load_night(edf, xml, cohort) -> dict(eeg, eog_l, eog_r, emg, spo2, stages, fs, id, cohort) or None.
Signals in uV (SpO2 in %), EEG/EMG at 100 Hz, EOG at 50 Hz, SpO2 at 1 Hz, truncated to the
scored epoch count. stages: int8 per 30 s epoch, 0=W 1=N1 2=N2 3=N3 4=R, -1=unscored/movement.
CLI: python nsrr_load.py --nsrr /tmp/nsrr-dev --out /tmp/nsrr-dev/nights
"""
import argparse, glob, os, sys
import xml.etree.ElementTree as ET
import numpy as np
import pyedflib
from scipy.signal import resample_poly

EPOCH = 30
FS = {"eeg": 100, "emg": 100, "eog": 50, "spo2": 1}
# label alternates, first match wins. SHHS: "EEG" is C4-A1; the EEG(sec)/EEG 2/EEG2 variants are C3-A2 and
# are only used as a logged fallback when C4 is absent.
CHANNELS = {
    "shhs": {"eeg": ["EEG", "EEG C4-A1", "C4-A1", "EEG(sec)", "EEG(SEC)", "EEG 2", "EEG2"], "eog_l": ["EOG(L)", "EOG-L"], "eog_r": ["EOG(R)", "EOG-R"],
             "emg": ["EMG", "EMG Chin"], "spo2": ["SaO2", "SpO2"]},
    "mesa": {"eeg": ["EEG3", "C4-M1"], "eog_l": ["EOG-L"], "eog_r": ["EOG-R"], "emg": ["EMG"], "spo2": ["SpO2"]},
}
STAGE = {"Wake|0": 0, "Stage 1 sleep|1": 1, "Stage 2 sleep|2": 2, "Stage 3 sleep|3": 3, "Stage 4 sleep|4": 3,
         "REM sleep|5": 4}  # Unscored|9, Movement|6 -> -1
UNIT_TO_UV = {"uv": 1.0, "µv": 1.0, "mv": 1000.0, "v": 1e6}
MIN_TST_H = 3.0


def parse_xml(path):
    """-> (stages int8 array, list of (start_s, dur_s) SpO2-artifact spans, recording duration s)."""
    root = ET.parse(path).getroot()
    events = root.findall(".//ScoredEvent")
    dur_total = None
    for ev in events:
        if (ev.findtext("EventConcept") or "") == "Recording Start Time":
            dur_total = float(ev.findtext("Duration"))
    stage_ev, art = [], []
    for ev in events:
        et, ec = ev.findtext("EventType") or "", ev.findtext("EventConcept") or ""
        s, d = float(ev.findtext("Start") or 0), float(ev.findtext("Duration") or 0)
        if et.startswith("Stages"):
            stage_ev.append((s, d, STAGE.get(ec, -1)))
        elif "SpO2 artifact" in ec:
            art.append((s, d))
    if not stage_ev:
        return None, art, dur_total
    end = max(s + d for s, d, _ in stage_ev)
    n = int(round(end / EPOCH))
    stages = np.full(n, -1, np.int8)
    for s, d, lab in stage_ev:  # Duration covers multi-epoch runs; expand
        a, b = int(round(s / EPOCH)), int(round((s + d) / EPOCH))
        stages[a:b] = lab
    return stages, art, dur_total


def _pick(labels, cands):
    """-> (signal index, candidate rank) of the first candidate present, else (None, None)."""
    low = [l.strip().lower() for l in labels]
    for k, c in enumerate(cands):
        if c.lower() in low:
            return low.index(c.lower()), k
    return None, None


def _resample(x, fs_in, fs_out):
    if fs_in == fs_out:
        return x.astype(np.float32)
    from math import gcd
    g = gcd(int(fs_in), int(fs_out))
    return resample_poly(x, int(fs_out) // g, int(fs_in) // g).astype(np.float32)


def load_night(edf, xml, cohort, log=print):
    nid = os.path.basename(edf).replace(".edf", "")
    stages, art, _ = parse_xml(xml)
    if stages is None:
        log(f"skip {nid}: no stage events"); return None
    try:
        r = pyedflib.EdfReader(edf)
    except OSError as e:
        log(f"skip {nid}: EDF open failed ({e})"); return None
    try:
        labels = r.getSignalLabels()
        out = {"id": nid, "cohort": cohort, "fs": dict(FS)}
        for key, cands in CHANNELS[cohort].items():
            i, rank = _pick(labels, cands)
            if i is None:
                log(f"skip {nid}: missing {key} among {labels}"); return None
            x = r.readSignal(i).astype(np.float64)
            unit = (r.getPhysicalDimension(i) or "uV").strip().lower()
            if key != "spo2":
                x *= UNIT_TO_UV.get(unit, 1.0)
            if key == "eeg":
                if rank >= 3 and cohort == "shhs":
                    log(f"note {nid}: C4 missing, using {labels[i]} (C3-A2)")
                out["rail"] = abs(r.getPhysicalMaximum(i)) * UNIT_TO_UV.get(unit, 1.0)  # ADC clip level, uV
            fs_in = int(round(r.getSampleFrequency(i)))
            fs_out = FS["eog" if key.startswith("eog") else key]
            if fs_in < fs_out:
                log(f"skip {nid}: {key} fs {fs_in} < {fs_out}"); return None
            out[key] = _resample(x, fs_in, fs_out)
    finally:
        r.close()
    # SpO2 artifact handling: XML spans + physiologic floor -> NaN
    sp = out["spo2"]
    for s, d in art:
        sp[int(s):int(np.ceil(s + d))] = np.nan
    sp[(sp < 50) | (sp > 100)] = np.nan
    # truncate everything to min(scored epochs, EDF epochs)
    n = min(len(stages), *[len(out[k]) // (EPOCH * out["fs"]["eog" if k.startswith("eog") else k])
                            for k in ("eeg", "eog_l", "eog_r", "emg", "spo2")])
    if n < len(stages):
        log(f"note {nid}: XML {len(stages)} epochs, EDF {n}; truncating")
    stages = stages[:n]
    for k in ("eeg", "eog_l", "eog_r", "emg", "spo2"):
        out[k] = out[k][: n * EPOCH * out["fs"]["eog" if k.startswith("eog") else k]]
    out["stages"] = stages
    tst_h = np.sum((stages >= 1) & (stages <= 4)) * EPOCH / 3600
    if tst_h < MIN_TST_H:
        log(f"skip {nid}: TST {tst_h:.1f} h < {MIN_TST_H}"); return None
    assert len(out["eeg"]) == n * EPOCH * FS["eeg"]
    return out


def find_pairs(root):
    """Yield (edf, xml, cohort) for every EDF under root with a matching -nsrr.xml."""
    for edf in sorted(glob.glob(os.path.join(root, "**", "*.edf"), recursive=True)):
        nid = os.path.basename(edf)[:-4]
        cohort = "shhs" if nid.startswith("shhs") else "mesa" if nid.startswith("mesa") else None
        xmls = glob.glob(os.path.join(root, "**", f"{nid}-nsrr.xml"), recursive=True)
        if cohort and xmls:
            yield edf, xmls[0], cohort


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsrr", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ok = 0
    for edf, xml, cohort in find_pairs(a.nsrr):
        nt = load_night(edf, xml, cohort)
        if nt is None:
            continue
        hist = np.bincount(nt["stages"][nt["stages"] >= 0], minlength=5)
        print(f"{nt['id']} {cohort} epochs={len(nt['stages'])} W/N1/N2/N3/R={hist.tolist()} "
              f"unscored={(nt['stages'] < 0).sum()} spo2_nan={np.isnan(nt['spo2']).mean():.3f}")
        np.savez_compressed(os.path.join(a.out, nt["id"] + ".npz"), **{k: v for k, v in nt.items() if k != "fs"},
                            fs_eeg=FS["eeg"], fs_eog=FS["eog"], fs_emg=FS["emg"], fs_spo2=FS["spo2"])
        ok += 1
    print(f"loaded {ok} nights -> {a.out}")
    sys.exit(0 if ok else 1)
