# nk-bin
## Generate WinCE boot images to run custom code

`nk_bin.py` provides a way of running custom code on devices with an unmodifiable bootloader designed to load Windows CE. It generates an `NK.bin` file that contains a user specified binary where the bootloader would expect to find the WinCE kernel.

This tool was designed to be used with an Omnitech car GPS (model 16878-US), to allow U-Boot to be loaded. The GPS has a bootloader on a flash chip, which was not easily writable through any debug interface. This bootloader then loads `NK.bin` from a FAT partition on the SD card. See [my blog](https://www.benwolsieffer.com/blog/omnitech_gps/part_1/) for more information about this device.

The tool currently hardcodes the addresses used on my device, but they could easily be modified or exposed as command line arguments.

`patch_nk_bin.py` replaces the WinCE kernel with the specified code within an existing `NK.bin` file. This was used for initial testing, when I wasn't sure if I could successfully generate a valid `NK.bin` file from scratch. I had very little debugging output from the device, so I wanted to eliminate as many possibilities for things to go wrong as I could.