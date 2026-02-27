#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞💾 OpenClaw Snapshot
智能备份与恢复工具 - 备份虾出品
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openclaw-snapshot",
    version="1.0.1",
    author="Duka Works",
    author_email="chenzhy.bj@gmail.com",
    description="🦞💾 OpenClaw 智能备份与恢复工具 - 留住每一刻",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dukaworks/openclaw-snapshot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "openclaw-snapshot=openclaw_snapshot.snapshot:main",
            "ocs=openclaw_snapshot.snapshot:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
