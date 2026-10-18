#!/usr/bin/env bash
# Confine untrusted authentic saved stage-2 programs to the approved MASCOT sandbox.
set -euo pipefail
image_name="${1:?Stage-2 evaluator image required}"
result_dir="${2:?Empty results directory required}"
shift 2
mkdir -p "$result_dir"
if [ -n "$(ls -A "$result_dir")" ]; then
  echo "Stage-2 replay rejects nonempty result directories" >&2
  exit 1
fi
result_dir="$(realpath "$result_dir")"
chmod 0777 "$result_dir"
image_id="$(docker image inspect --format '{{.Id}}' "$image_name")"
revision="$(git rev-parse HEAD)"
docker run --rm --network none --read-only --user 1000:1000 \
  --cap-drop ALL --security-opt no-new-privileges \
  --cpus 2 --memory 6g --memory-swap 6g --pids-limit 256 \
  --tmpfs /run:rw,nosuid,nodev,size=3g,uid=1000,gid=1000,mode=0700 \
  --tmpfs /tmp:rw,nosuid,nodev,size=256m,uid=1000,gid=1000,mode=0700 \
  --tmpfs /baseline/evaluation/evaluation_storage:rw,nosuid,nodev,size=64m,uid=1000,gid=1000,mode=0700 \
  --mount "type=bind,source=$result_dir,target=/results" \
  --env REPLAY_CONTAINER=1 --env "RESEARCH_COMMIT=$revision" \
  --env "REPLAY_IMAGE_ID=$image_id" \
  --entrypoint python "$image_id" /harness/replay_stage2.py "$@"
