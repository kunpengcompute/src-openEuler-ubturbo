#!/bin/bash
#
# build-deb.sh - Build Debian binary packages for ubturbo from the upstream
#                tarball, using the debian/ packaging directory shipped in
#                this repository.
#
# Usage:   ./build-deb.sh [KVER]
#          KVER=<ver> ./build-deb.sh
# Output:  ../  (parent of the script/source directory) containing *.deb,
#           *.changes and *.buildinfo
#
# Optional:
#   KVER   Kernel version to build against (e.g. 6.6.0-...). When omitted the
#          newest /lib/modules/<ver>/build on the host is selected.
#
# The script is idempotent and does not depend on the caller's working
# directory: all paths are resolved relative to this script's location.

set -euo pipefail

# Kernel version may be passed as the first positional argument or via the
# KVER environment variable. Positional argument takes precedence.
if [ "$#" -ge 1 ] && [ -n "$1" ]; then
    KVER="$1"
fi
export KVER="${KVER:-}"

# Print a formatted error message and exit.
die() {
    echo "E: $*" >&2
    exit 1
}

# Locate script directory deterministically so the build does not depend on
# the caller's working directory.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pkg_name="ubturbo"
pkg_version="1.0.0"
orig_tar="${pkg_name}-${pkg_version}.tar.gz"
source_dir="${pkg_name}-${pkg_version}"
output_dir="${script_dir}/.."

# Validate prerequisites.
[ -f "${script_dir}/${orig_tar}" ]   || die "Upstream tarball not found: ${script_dir}/${orig_tar}"
[ -d "${script_dir}/debian" ]       || die "debian/ directory not found in ${script_dir}"

echo "I: Building ${pkg_name} ${pkg_version} from ${script_dir}"

# Fresh source tree per run.
rm -rf "${script_dir}/${source_dir}"
mkdir -p "${script_dir}/${source_dir}"
cd "${script_dir}/${source_dir}"

echo "I: Extracting upstream tarball"
tar -xzf "${script_dir}/${orig_tar}" --strip-components=1

echo "I: Converting CRLF to LF in source files"
find . -type f \( -name "*.c" -o -name "*.h" -o -name "*.cpp" -o -name "Makefile" -o -name "*.spec" -o -name "*.txt" \) \
    -exec sed -i 's/\r$//' {} \;

echo "I: Copying debian/ packaging"
cp -a "${script_dir}/debian" ./debian
# Remove dh_make template leftovers if any.
rm -f debian/*.ex debian/*.EX

# Apply quilt patches declared in debian/patches/series. With source format
# 3.0 (quilt) and a binary-only build, dpkg-buildpackage does NOT apply
# patches on its own, so we ask dpkg-source to do it explicitly. This is the
# lintian-clean way (no patch handling inside debian/rules).
#
# Strip any CR characters from patch files first: if the debian/ tree was
# edited on Windows the patches may have CRLF line endings, which cause
# context mismatch against the LF-only upstream sources.
echo "I: Normalising patch line endings to LF"
if [ -d debian/patches ]; then
    find debian/patches -type f \( -name '*.patch' -o -name 'series' \) \
        -exec sed -i 's/\r$//' {} +
fi

echo "I: Applying quilt patches via dpkg-source --before-build"
dpkg-source --before-build .

# Pre-flight: make sure a kernel build tree is available for the kmod build.
# When KVER is provided, verify the exact /lib/modules/<KVER>/build exists;
# otherwise auto-select the newest /lib/modules/*/build symlink. Filtering on
# the "build" symlink avoids picking up non-kernel directories (smap, ucache)
# that this very package installs under /lib/modules.
if [ -n "${KVER}" ]; then
    kdir="/lib/modules/${KVER}/build"
    [ -d "${kdir}" ] || die "Requested kernel build tree not found: ${kdir}
Install the matching linux-headers-${KVER} package, or run without arguments
to auto-select the newest available kernel build tree."
    echo "I: Using requested kernel ${KVER} (build tree: ${kdir})"
else
    if ! ls -d /lib/modules/*/build >/dev/null 2>&1; then
        die "No kernel build tree found under /lib/modules/*/build. Install the matching linux-headers-* package for the running kernel before building, or pass KVER explicitly."
    fi
    echo "I: Using newest kernel build tree: $(ls -d /lib/modules/*/build 2>/dev/null | sort -V | tail -n 1)"
fi

echo "I: Building binary packages with dpkg-buildpackage"
# Build as binary-only, no signing, allow rootless build via fakeroot.
# KVER is exported so debian/rules picks it up.
dpkg-buildpackage -rfakeroot -us -uc -b

# Collect build artifacts into the parent of the script/source directory.
# dpkg-buildpackage emits *.deb/*.changes/*.buildinfo into the parent of the
# build tree, which is ${script_dir} itself; move them up one more level to
# ${output_dir} (= ${script_dir}/..).
cd "${script_dir}"

shopt -s nullglob
found_artifact=0
for f in ./*.deb ./*.changes ./*.buildinfo ./*.ddeb; do
    [ -e "$f" ] || continue
    mv "$f" "${output_dir}/"
    found_artifact=1
    echo "I: Collected $(basename "$f")"
done
shopt -u nullglob

[ "$found_artifact" -eq 1 ] || die "No .deb/.changes/.buildinfo produced by dpkg-buildpackage"

echo "I: Build complete. Artifacts in: ${output_dir}"
ls -l "${output_dir}"
