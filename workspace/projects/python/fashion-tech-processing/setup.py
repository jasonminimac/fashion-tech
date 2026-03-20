"""Setup configuration for fashion-tech-processing package."""

from setuptools import setup, find_packages

setup(
    name="fashion-tech-processing",
    version="0.1.0",
    description="3D body scan point cloud processing pipeline",
    author="3D Scanning Lead",
    author_email="team@fashiontech.local",
    url="https://fashiontech.local/processing",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "open3d>=0.17.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "trimesh>=3.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ftp-process=pipeline.pipeline:main",
        ],
    },
)
