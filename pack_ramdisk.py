#!/usr/bin/env python3
"""
Pack a ramdisk source tree (CM7/, CMX/, Stock/) into an Android-style
newc cpio archive with the permissions/ownership actually used by the
known-working ThunderKernel 2.2 boot.img, then LZMA-compress it.

git can only track 644/755/120000 modes, so the checked-out source
tree always has slightly wrong permissions (e.g. /sbin and everything
under it should be 0750, not 0755/0644, and /data should be 0771, not
0755). This script reapplies the verified real scheme at pack time
instead of relying on the working tree's on-disk modes, and always
sets ownership to root:root (uid/gid 0) since cpio archives extracted
by init run before any other user exists.

Usage: pack_ramdisk.py <src_dir> <output.cpio.lzma>
"""
import os
import struct
import subprocess
import sys

# Verified against the real ThunderKernel 2.2 Stock boot.img ramdisk.
SBIN_DIR_MODE = 0o750
SBIN_FILE_MODE = 0o750
INIT_FILE_MODE = 0o750
DATA_DIR_MODE = 0o771
DEFAULT_DIR_MODE = 0o755
DEFAULT_FILE_MODE = 0o644

INIT_FILENAMES = {
    "init", "init.rc", "init.bcm21553.rc", "init.charge.rc",
    "init.goldfish.rc",
}


def mode_for(relpath, is_dir, is_symlink):
    parts = relpath.split("/")
    top = parts[0]

    if is_symlink:
        # Symlinks under sbin/ (sh, ueventd) match the reference's 0750.
        if top == "sbin":
            return 0o120750
        return 0o120755

    if is_dir:
        if relpath == "data":
            return 0o040000 | DATA_DIR_MODE
        if top == "sbin":
            return 0o040000 | SBIN_DIR_MODE
        return 0o040000 | DEFAULT_DIR_MODE

    if top == "sbin":
        return 0o100000 | SBIN_FILE_MODE
    if len(parts) == 1 and parts[0] in INIT_FILENAMES:
        return 0o100000 | INIT_FILE_MODE
    return 0o100000 | DEFAULT_FILE_MODE


# Placeholder files that only exist so git tracks otherwise-empty
# mountpoint directories (data/, dev/, proc/, sys/, tmp/) - the real
# shipped ramdisk never contains these.
SKIP_NAMES = {".gitignore", ".DS_Store"}


def walk_sorted(src_dir):
    """Yield (relpath, abspath) for every entry, directories immediately
    before their contents, everything else alphabetical - matching the
    order mkbootfs/the reference image uses."""
    def _walk(rel):
        absdir = os.path.join(src_dir, rel) if rel else src_dir
        names = sorted(n for n in os.listdir(absdir) if n not in SKIP_NAMES)
        for name in names:
            entry_rel = f"{rel}/{name}" if rel else name
            entry_abs = os.path.join(absdir, name)
            if os.path.islink(entry_abs):
                yield entry_rel, entry_abs
            elif os.path.isdir(entry_abs):
                yield entry_rel, entry_abs
                yield from _walk(entry_rel)
            else:
                yield entry_rel, entry_abs
    yield from _walk("")


def cpio_newc_header(name, mode, filesize, ino):
    namesize = len(name) + 1  # + NUL
    # ino, mode, uid, gid, nlink, mtime, filesize,
    # devmajor, devminor, rdevmajor, rdevminor, namesize, check (13 fields)
    fields = [
        ino, mode, 0, 0, 1, 0,
        filesize, 0, 0, 0, 0,
        namesize, 0,
    ]
    header = "070701" + "".join(f"{f:08X}" for f in fields)
    entry = header.encode("ascii") + name.encode("utf-8") + b"\x00"
    pad = (-len(entry)) % 4
    return entry + b"\x00" * pad


def cpio_pad_data(data):
    pad = (-len(data)) % 4
    return data + b"\x00" * pad


def build_cpio(src_dir):
    out = bytearray()
    ino = 1
    for relpath, abspath in walk_sorted(src_dir):
        is_symlink = os.path.islink(abspath)
        is_dir = (not is_symlink) and os.path.isdir(abspath)
        mode = mode_for(relpath, is_dir, is_symlink)

        if is_symlink:
            target = os.readlink(abspath).encode("utf-8")
            out += cpio_newc_header(relpath, mode, len(target), ino)
            out += cpio_pad_data(target)
        elif is_dir:
            out += cpio_newc_header(relpath, mode, 0, ino)
        else:
            with open(abspath, "rb") as f:
                data = f.read()
            out += cpio_newc_header(relpath, mode, len(data), ino)
            out += cpio_pad_data(data)
        ino += 1

    out += cpio_newc_header("TRAILER!!!", 0, 0, 0)
    # cpio archives are padded to a 512-byte boundary by convention.
    pad = (-len(out)) % 512
    out += b"\x00" * pad
    return bytes(out)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    src_dir, out_path = sys.argv[1], sys.argv[2]
    if not os.path.isdir(src_dir):
        print(f"error: {src_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    cpio_data = build_cpio(src_dir)

    lzma_proc = subprocess.run(
        ["xz", "-9", "-e", "--format=lzma", "-c"],
        input=cpio_data, stdout=subprocess.PIPE, check=True,
    )

    with open(out_path, "wb") as f:
        f.write(lzma_proc.stdout)

    print(f"{src_dir} -> {out_path} "
          f"(cpio {len(cpio_data)} bytes, lzma {len(lzma_proc.stdout)} bytes)")


if __name__ == "__main__":
    main()
