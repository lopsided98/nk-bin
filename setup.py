from mypyc.build import mypycify
from setuptools import setup

setup(
    name='nk-bin',
    version='0.1',
    description=" Generate WinCE boot images to run custom code",
    author="Ben Wolsieffer",
    author_email='benwolsieffer@gmail.com',
    license='GPLv3',

    ext_modules=mypycify(['nk_bin.py', 'patch_nk_bin.py']),
    entry_points={
        'console_scripts': [
            'nk-bin=nk_bin:main',
            'patch-nk-bin=patch_nk_bin:main'
        ],
    },

    setup_requires=['mypy'],
)
