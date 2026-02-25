#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="chalilulz",
    version="0.0.1b2",
    py_modules=["chalilulz"],
    install_requires=[],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "chalilulz=chalilulz:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8+",
    ],
)
