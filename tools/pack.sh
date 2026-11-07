#!/usr/bin/env bash
# Build claude.ai upload zips: dist/<skill>.zip, one per skill (or only the ones named).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
skills=("$@")
[[ ${#skills[@]} -gt 0 ]] || skills=($(ls skills))
for skill in "${skills[@]}"; do
  [[ -f "skills/$skill/SKILL.md" ]] || { echo "no such skill: $skill" >&2; exit 1; }
  rm -f "dist/$skill.zip"
  (cd skills && zip -rq "../dist/$skill.zip" "$skill" -x '*.DS_Store')
  echo "dist/$skill.zip"
done
