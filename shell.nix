{ pkgs ? import <nixpkgs> { } }:

pkgs.python3Packages.callPackage ./. {
  nixShell = true;
}
