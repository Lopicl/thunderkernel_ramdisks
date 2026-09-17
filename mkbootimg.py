#!/usr/bin/env python3
"""
Minimal Android boot.img packer for the cooperve (GT-S5830i) BCM21553
platform, reverse-engineered from a known-working ThunderKernel 2.2
boot.img (base=0x81600000, pagesize=4096, standard kernel/ramdisk/tags
offsets 0x00008000/0x01000000/0x00000100, empty on-image cmdline since
this kernel's CONFIG_CMDLINE is baked in).

Usage:
  mkbootimg.py --kernel zImage --ramdisk ramdisk.lzma -o boot.img
               [--base 0x81600000] [--pagesize 4096] [--cmdline "..."]
"""
import argparse
import hashlib
import struct
import sys

BOOT_MAGIC = b"ANDROID!"


def pad_to_page(data, page_size):
    pad = (-len(data)) % page_size
    return data + b"\x00" * pad


def build_boot_image(kernel, ramdisk, second, base, page_size,
                      kernel_offset, ramdisk_offset, second_offset,
                      tags_offset, cmdline, board_name):
    kernel_addr = base + kernel_offset
    ramdisk_addr = base + ramdisk_offset
    second_addr = base + second_offset
    tags_addr = base + tags_offset

    cmdline_bytes = cmdline.encode("utf-8")
    if len(cmdline_bytes) > 512:
        raise ValueError("cmdline too long (max 512 bytes)")
    board_bytes = board_name.encode("utf-8")
    if len(board_bytes) > 16:
        raise ValueError("board name too long (max 16 bytes)")

    # id = sha1(kernel + kernel_size + ramdisk + ramdisk_size +
    #           second + second_size), matching Android's mkbootimg.
    h = hashlib.sha1()
    h.update(kernel)
    h.update(struct.pack("<I", len(kernel)))
    h.update(ramdisk)
    h.update(struct.pack("<I", len(ramdisk)))
    h.update(second)
    h.update(struct.pack("<I", len(second)))
    digest = h.digest()
    id_field = digest[:20] + b"\x00" * (32 - len(digest))

    header = bytearray(608)
    struct.pack_into("<8s", header, 0, BOOT_MAGIC)
    struct.pack_into(
        "<10I", header, 8,
        len(kernel), kernel_addr,
        len(ramdisk), ramdisk_addr,
        len(second), second_addr,
        tags_addr, page_size,
        0, 0,  # dt_size, unused
    )
    struct.pack_into("<16s", header, 48, board_bytes)
    struct.pack_into("<512s", header, 64, cmdline_bytes)
    struct.pack_into("<32s", header, 576, id_field)

    assert len(header) == 608

    out = bytearray()
    out += pad_to_page(bytes(header), page_size)
    out += pad_to_page(kernel, page_size)
    out += pad_to_page(ramdisk, page_size)
    if second:
        out += pad_to_page(second, page_size)
    return bytes(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kernel", required=True)
    p.add_argument("--ramdisk", required=True)
    p.add_argument("--second", default=None)
    p.add_argument("--base", default="0x81600000")
    p.add_argument("--pagesize", type=int, default=4096)
    p.add_argument("--kernel_offset", default="0x00008000")
    p.add_argument("--ramdisk_offset", default="0x01000000")
    p.add_argument("--second_offset", default="0x00f00000")
    p.add_argument("--tags_offset", default="0x00000100")
    p.add_argument("--cmdline", default="")
    p.add_argument("--board", default="")
    p.add_argument("-o", "--output", required=True)
    args = p.parse_args()

    with open(args.kernel, "rb") as f:
        kernel = f.read()
    with open(args.ramdisk, "rb") as f:
        ramdisk = f.read()
    second = b""
    if args.second:
        with open(args.second, "rb") as f:
            second = f.read()

    image = build_boot_image(
        kernel, ramdisk, second,
        base=int(args.base, 0),
        page_size=args.pagesize,
        kernel_offset=int(args.kernel_offset, 0),
        ramdisk_offset=int(args.ramdisk_offset, 0),
        second_offset=int(args.second_offset, 0),
        tags_offset=int(args.tags_offset, 0),
        cmdline=args.cmdline,
        board_name=args.board,
    )

    with open(args.output, "wb") as f:
        f.write(image)

    print(f"wrote {args.output} ({len(image)} bytes)")


if __name__ == "__main__":
    main()
