# RunPod pod settings (10 lines)

1. GPU: `2x H100 80GB SXM` (one pod, 2 GPUs). Nothing bigger; ~15-20 GPU-hours total.
2. Template: custom image `runpod/pytorch:2.6-py3.12-cuda-12.1` (same base as `Dockerfile.runpod`).
3. Container disk: 50 GB. Volume: 200 GB mounted at `/workspace` (repo, HF cache, NSRR EDFs, logs all live here and survive restarts).
4. Expose TCP ports: `22` (ssh) and `8000` (vLLM target).
5. Env vars: do NOT paste secrets into the RunPod UI. Put them in `/workspace/loki/handoff/.env` after first ssh; scripts source it.
6. Do NOT set `CUDA_VISIBLE_DEVICES` globally in the pod template. Each script sets it per process (GPU0 = vLLM target + B3, GPU1 = B4 then sleep).
7. Start command: leave default (ssh). Jupyter not needed.
8. First command after ssh: `git clone -b agentwild-pivot https://github.com/yashthakur2008/arpandeep-nrty.git /workspace/loki && cd /workspace/loki && cp handoff/.env.example handoff/.env && nano handoff/.env`
9. Then: `bash handoff/bootstrap.sh` (idempotent, ~15 min first run, mostly model download).
10. Then follow `handoff/HANDOFF.md` section 4. Stop the pod when both `run_*.sh` print DONE; the volume keeps everything.
