#!/usr/bin/env python3
"""Entry program for news-image-20261119.

Copies the pre-rendered front page (entry.png) to the output directory,
then validates the copy: PNG header, 1024x1024 dimensions, and a sha256
match against the source, so a bad copy can never pass silently.
"""
import hashlib
import os
import shutil
import struct
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def png_dimensions(path):
    with open(path, "rb") as f:
        head = f.read(33)
    if head[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file: bad magic bytes")
    if head[12:16] != b"IHDR":
        raise ValueError("not a PNG file: missing IHDR chunk")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    width, height = png_dimensions(dst)
    if (width, height) != (1024, 1024):
        raise ValueError("entry.png must be 1024x1024, got %dx%d"
                         % (width, height))
    src_hash = sha256_file(src)
    dst_hash = sha256_file(dst)
    if src_hash != dst_hash:
        raise ValueError("output sha256 does not match source")
    size = os.path.getsize(dst)
    print("wrote %s (%dx%d, %d bytes, sha256 %s)"
          % (dst, width, height, size, dst_hash))


if __name__ == "__main__":
    main()
