#!/usr/bin/env bash
set -u

usage() {
  echo "usage: compile-package.sh <skill-package-dir> [registry-dir]" >&2
  exit 2
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  usage
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd) || {
  echo "compile-package: cannot resolve script directory" >&2
  exit 3
}
skills_root=$(CDPATH= cd -- "$script_dir/../../../.." 2>/dev/null && pwd) || {
  echo "compile-package: cannot resolve connectionagent-skills root" >&2
  exit 3
}

platform_hint=${CONNECTIONAGENT_SKILL_PLATFORM:-"$skills_root/../connectionagent-skill-platform"}
case "$platform_hint" in
  /*) platform_root=$platform_hint ;;
  *) platform_root="$skills_root/$platform_hint" ;;
esac
platform_root=$(CDPATH= cd -- "$platform_root" 2>/dev/null && pwd) || {
  echo "compile-package: Skill Platform checkout not found: $platform_hint" >&2
  echo "set CONNECTIONAGENT_SKILL_PLATFORM=/path/to/connectionagent-skill-platform" >&2
  exit 2
}

case "$1" in
  /*) package_dir=$1 ;;
  *) package_dir="$skills_root/$1" ;;
esac

if [ "$#" -eq 2 ]; then
  case "$2" in
    /*) registry_dir=$2 ;;
    *) registry_dir="$platform_root/$2" ;;
  esac
else
  registry_dir="$platform_root/registry"
fi

if [ ! -d "$package_dir" ]; then
  echo "compile-package: Skill package directory does not exist: $package_dir" >&2
  exit 2
fi
if [ ! -d "$registry_dir" ]; then
  echo "compile-package: Registry directory does not exist: $registry_dir" >&2
  exit 2
fi

if command -v go >/dev/null 2>&1; then
  temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/casp-skill-compile.XXXXXX") || exit 3
  trap 'rm -rf -- "$temp_dir"' EXIT
  casp_bin="$temp_dir/casp"
  (cd "$platform_root" && go build -o "$casp_bin" ./backend/cmd/casp) || {
    echo "compile-package: failed to build casp from Skill Platform" >&2
    exit 3
  }
elif [ -x "$platform_root/dist/casp" ]; then
  casp_bin="$platform_root/dist/casp"
elif command -v casp >/dev/null 2>&1; then
  casp_bin=$(command -v casp)
else
  echo "compile-package: casp CLI is unavailable and Go is not installed" >&2
  exit 2
fi

"$casp_bin" compile \
  --package "$package_dir" \
  --registry "$registry_dir" \
  --format json
exit $?
