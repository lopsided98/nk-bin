#!/usr/bin/env python3

import binascii
import struct
import sys
import time
from typing import BinaryIO, List, Optional

ROMHDR_PTR_FMT = "<I"
PTOC_FMT = "<I"

START_ADDR = 0x88200000
EXE_ADDR = START_ADDR + 0x1000
NAME_ADDR = 0x88A00000
ROMHDR_ADDR = 0x88E7B130


class B000FF:
    MAGIC = b"B000FF\n"
    HEADER_FMT = "<7sII"
    ENTRY_FMT = "<III"

    def __init__(self, file: BinaryIO):
        self._file = file

        self._start_addr = 2**32 - 1
        self._end_addr = 0

        self._exec_addr = 0

        self._file.seek(struct.calcsize(self.HEADER_FMT))

    def add_entry(self, addr: int, data: bytes) -> None:
        assert addr >= self._end_addr

        if addr < self._start_addr:
            self._start_addr = addr
        if addr + len(data) > self._end_addr:
            self._end_addr = addr + len(data)

        self._file.write(struct.pack(self.ENTRY_FMT, addr, len(data), sum(data)))
        self._file.write(data)

    def set_exec_address(self, addr: int) -> None:
        self._exec_addr = addr

    def finalize(self) -> None:
        # Write execution start record
        self._file.write(struct.pack(self.ENTRY_FMT, 0, self._exec_addr, 0))

        # Write header
        self._file.seek(0)

        length = self._end_addr - self._start_addr
        assert length >= 0

        self._file.write(
            struct.pack(self.HEADER_FMT, self.MAGIC, self._start_addr, length)
        )


class TOCEntry:
    FMT = "<IQIIIII"
    SIZE = struct.calcsize(FMT)

    def __init__(
        self,
        size: int,
        name_ptr: int,
        attrs: int = 0x7,
        epoch_time: Optional[float] = None,
        e32_ptr: int = 0x0,
        o32_ptr: int = 0x0,
        load_ptr: int = 0x0,
    ):
        time = self.to_toc_time(epoch_time)
        self.data = struct.pack(
            self.FMT, attrs, time, size, name_ptr, e32_ptr, o32_ptr, load_ptr
        )

    @staticmethod
    def to_toc_time(epoch_time: Optional[float] = None) -> int:
        if epoch_time is None:
            epoch_time = time.time()
        return int((epoch_time + 11644473600) * 10000000)


class TOC:
    ROMHDR_FMT = "<IIIIIIIIIIIIIIIIIHHIII"
    HEADER_SIZE = struct.calcsize(ROMHDR_FMT)

    def __init__(
        self,
        phys_first: int,
        # Set correctly once known
        phys_last: int = 0x0,
        # These probably don't matter much unless you are actually
        # booting WinCE. I just took the values from the original
        # NK.bin
        dll_first: int = 0x1EE01EE,
        dll_last: int = 0x2000000,
        ram_start: int = 0x88E80000,
        ram_free: int = 0x88EEA000,
        ram_end: int = 0x8C000000,
        copy_entries: int = 0x0,
        copy_offset: int = 0x0,
        profile_len: int = 0x0,
        profile_offset: int = 0x0,
        kernel_flags: int = 0x2,
        fs_ram_percent: int = 0x03030303,
        driv_glob_start: int = 0x0,
        driv_glob_len: int = 0x0,
        cpu_type: int = 0x1C2,
        misc_flags: int = 0x2,
        extensions_ptr: int = 0x88202F60,  # invalid
        tracking_start: int = 0x0,
        tracking_len: int = 0x0,
    ) -> None:

        # Make sure I got the right number of
        assert self.HEADER_SIZE == 84

        self.dll_first = dll_first
        self.dll_last = dll_last
        self.phys_first = phys_first
        self.phys_last = phys_last
        self.num_mods = 0
        self.ram_start = ram_start
        self.ram_free = ram_free
        self.ram_end = ram_end
        self.copy_entries = copy_entries
        self.copy_offset = copy_offset
        self.profile_len = profile_len
        self.profile_offset = profile_offset
        self.num_files = 0
        self.kernel_flags = kernel_flags
        self.fs_ram_percent = fs_ram_percent
        self.driv_glob_start = driv_glob_start
        self.driv_glob_len = driv_glob_len
        self.cpu_type = cpu_type
        self.misc_flags = misc_flags
        self.extensions_ptr = extensions_ptr
        self.tracking_start = tracking_start
        self.tracking_len = tracking_len

        self._entries: List[TOCEntry] = []

    def add_entry(self, entry: TOCEntry) -> None:
        self._entries.append(entry)

        self.num_mods += 1
        # In WinCE, this is not equal to num_mods?
        self.num_files += 1

    @property
    def data(self) -> bytearray:
        buf = bytearray(
            struct.pack(
                self.ROMHDR_FMT,
                self.dll_first,
                self.dll_last,
                self.phys_first,
                self.phys_last,
                self.num_mods,
                self.ram_start,
                self.ram_free,
                self.ram_end,
                self.copy_entries,
                self.copy_offset,
                self.profile_len,
                self.profile_offset,
                self.num_files,
                self.kernel_flags,
                self.fs_ram_percent,
                self.driv_glob_start,
                self.driv_glob_len,
                self.cpu_type,
                self.misc_flags,
                self.extensions_ptr,
                self.tracking_start,
                self.tracking_len,
            )
        )
        for entry in self._entries:
            buf.extend(entry.data)
        return buf

    @property
    def size(self) -> int:
        return self.HEADER_SIZE + len(self._entries) * TOCEntry.SIZE


def main() -> None:
    exe_path = sys.argv[1]
    with open(exe_path, "rb") as exe_file:
        exe_buf = exe_file.read()

    file = open("NK.bin", "wb")

    b000ff = B000FF(file)

    # Jump forward by 0x1000
    b000ff.add_entry(START_ADDR, bytes((0xFE, 0x03, 0x00, 0xEA)))

    # ROMHDR pointer
    b000ff.add_entry(START_ADDR + 0x40, b"ECEC" + struct.pack("<I", ROMHDR_ADDR))
    # pTOC (relative pointer to ROMHDR). No idea whether this really needs to
    # be a separate entry
    b000ff.add_entry(START_ADDR + 0x48, struct.pack("<I", ROMHDR_ADDR - START_ADDR))

    # Add the actual executable code
    b000ff.add_entry(EXE_ADDR, exe_buf)

    # Add the file name pointed to by the TOC
    # Address probably doesn't matter.
    b000ff.add_entry(NAME_ADDR, b"nk.exe\0")

    # ROMHDR/TOC seems to be used by the bootloader to find nk.exe
    toc = TOC(START_ADDR)
    toc.add_entry(TOCEntry(size=len(exe_buf), name_ptr=NAME_ADDR))
    toc.phys_last = ROMHDR_ADDR + toc.size

    b000ff.add_entry(ROMHDR_ADDR, toc.data)

    # Doesn't seem to be used, but supposed to be there
    b000ff.set_exec_address(EXE_ADDR)
    b000ff.finalize()


if __name__ == "__main__":
    main()
