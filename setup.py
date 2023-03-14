from setuptools import setup

setup(
    name="nk-bin",
    version="0.1.1",
    description="Generate WinCE boot images to run custom code",
    author="Ben Wolsieffer",
    author_email="benwolsieffer@gmail.com",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
    ],
    py_modules=["nk_bin", "patch_nk_bin"],
    entry_points={
        "console_scripts": ["nk-bin=nk_bin:main", "patch-nk-bin=patch_nk_bin:main"],
    },
)
