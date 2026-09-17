# ThunderKernel ramdisks

Ramdisk source trees for the Samsung Galaxy Ace i (GT-S5830i, codename
`cooperve`, BCM21553 platform), one per supported ROM:

- `CM7/` - CyanogenMod 7
- `CMX/` - CyanMobile X
- `Stock/` - Stock Samsung ROM

Each directory is the exact layout of a ramdisk as it should appear when
extracted into a boot.img: `init*`, `sbin/`, `res/`, etc. at the top level.

## Packing a ramdisk

git can only track file modes as `644`/`755`/`120000` (symlink), so the
checked-out permissions in these directories are close but not exactly
what a real device needs - notably `sbin/` and everything under it should
be `0750` (not world-executable), and `data/` should be `0771`. Don't rely
on the working tree's on-disk modes; always pack through the script below,
which reapplies the exact permission scheme verified against a known-good
ThunderKernel 2.2 `boot.img` (root:root ownership throughout):

| Path                          | Mode   |
|--------------------------------|--------|
| `sbin/` (dir) and everything under it | `0750` |
| `data/` (dir)                  | `0771` |
| `init`, `init.rc`, `init.bcm21553.rc`, `init.charge.rc`, `init.goldfish.rc` | `0750` |
| any other directory            | `0755` |
| any other file                 | `0644` |

```sh
python3 pack_ramdisk.py <CM7|CMX|Stock> <output.lzma>

# e.g.
python3 pack_ramdisk.py CM7 out/cm7_ramdisk.lzma
python3 pack_ramdisk.py CMX out/cmx_ramdisk.lzma
python3 pack_ramdisk.py Stock out/stock_ramdisk.lzma
```

This produces an Android-style `newc` cpio archive (matching what
`mkbootfs` produces) compressed with LZMA - the format this kernel/ramdisk
combination needs, not the more common gzip. Requires `xz` (`brew install
xz` if it isn't already on your PATH).

`.gitignore`/`.DS_Store` placeholder files (only present so git tracks
otherwise-empty mountpoint directories like `dev/`, `proc/`, `sys/`,
`tmp/`, `data/`) are automatically excluded from the packed archive.

## Building a boot.img

Once you have a compiled `zImage` (from the
[android_kernel_cooperve_thunder](https://github.com/Lopicl/android_kernel_cooperve_thunder)
repo) and a packed ramdisk from the step above, combine them with
`mkbootimg.py`:

```sh
python3 mkbootimg.py \
  --kernel /path/to/zImage \
  --ramdisk out/cm7_ramdisk.lzma \
  --base 0x81600000 \
  --pagesize 4096 \
  -o boot.img
```

`--base` and `--pagesize` are the values verified against a real,
known-working ThunderKernel 2.2 `boot.img` for this device; the kernel and
ramdisk offsets, tags offset, and empty on-image cmdline (this kernel's
command line is baked into its defconfig via `CONFIG_CMDLINE`, not read
from the boot image) all default to match that same reference and
shouldn't need to be overridden. Rebuilding a boot.img from that
reference's own extracted kernel and ramdisk with this script reproduces
it byte-for-byte.

Repeat once per ROM to produce `CM7`, `CMX`, and `Stock` boot.img files.

## Requirements

- Python 3 (no third-party packages required)
- `xz` on PATH for LZMA compression (`brew install xz` on macOS)
