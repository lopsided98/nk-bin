#!/usr/bin/env python3

import struct
import sys
from typing import Any, BinaryIO, Tuple

NK_EXE_ADDR = 0x88201000

OFFSET = 0x0

B000FF_MAGIC = b"B000FF\n"
B000FF_HEADER_FMT = "<7sII"
B000FF_ENTRY_FMT = "<III"


def unpack(stream: BinaryIO, fmt: str) -> Tuple[Any, ...]:
    size = struct.calcsize(fmt)
    buf = stream.read(size)
    return struct.unpack(fmt, buf)


def main() -> None:
    with open(sys.argv[1], 'rb') as new_exe_file:
        new_exe_buf = new_exe_file.read()

    file = open('NK.bin', 'rb+')

    magic, _, _ = unpack(file, B000FF_HEADER_FMT)

    assert magic == B000FF_MAGIC

    while True:
        file_offset = file.tell()
        addr, length, checksum = unpack(file, B000FF_ENTRY_FMT)
        print(addr)
        if addr == NK_EXE_ADDR:
            break
        file.seek(length, 1)
    print(f"Found nk.exe at offset {file_offset}")

    # New file must not be larger
    assert len(new_exe_buf) <= length

    exe_buf = bytearray(file.read(length))
    exe_buf[OFFSET:len(new_exe_buf) + OFFSET] = new_exe_buf

    checksum = sum(exe_buf)

    file.seek(file_offset)
    file.write(struct.pack(B000FF_ENTRY_FMT, addr, length, checksum))
    file.write(exe_buf)


if __name__ == "__main__":
    main()
