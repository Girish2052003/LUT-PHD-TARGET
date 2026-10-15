#!/usr/bin/env bash
# Run only the previously built, inspected original-source image.
set -euo pipefail
image_name="${1:?Image name required}"
result_dir="${2:?Fresh output directory required}"
shift 2
mkdir -p "$result_dir"
if [ -n "$(ls -A "$result_dir")" ]; then
    echo "Refusing to reuse a nonempty experiment directory" >&2
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
    "$image_id" "$@"
