#!/usr/bin/env bash
set -e
# Always run from the script's own directory
cd "$(dirname "$0")"

COMPANIES=(trilinc strata hp angi nvidia tesla apple harley)

usage() {
    echo "Usage: bash run_mindmaps.sh <company> [company2 ...] | bash run_mindmaps.sh all"
    echo "Companies: ${COMPANIES[*]}"
}

if [ $# -eq 0 ]; then
    usage
    exit 0
fi

if [ "$1" = "all" ]; then
    targets=("${COMPANIES[@]}")
else
    targets=("$@")
fi

for company in "${targets[@]}"; do
    found=0
    for c in "${COMPANIES[@]}"; do
        [ "$c" = "$company" ] && found=1 && break
    done
    if [ $found -eq 0 ]; then
        echo "Warning: Unknown company '$company' — skipping"
        continue
    fi
    echo "Generating mind map for $company..."
    python gen_mindmap.py "$company"
done
