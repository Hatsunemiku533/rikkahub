#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
patch_dir="$script_dir/../patch"
source_dir=$(cd -- "${1:?usage: apply-patches.sh upstream-directory}" && pwd)
for name in image-compress user-experience workspace-browser; do
  echo "::group::Validate and apply $name.patch"
  git -C "$source_dir" apply --check "$patch_dir/$name.patch"
  git -C "$source_dir" apply --whitespace=nowarn "$patch_dir/$name.patch"
  echo "::endgroup::"
done
git -C "$source_dir" diff --check
