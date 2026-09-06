#!/usr/bin/env bash
# Compatibility wrapper. The maintained RunPod path is deploy_runpod.sh.
set -euo pipefail
exec ./deploy_runpod.sh "$@"
