"""Setup script for psrcdataportal package."""

from pathlib import Path
from setuptools import setup, find_packages

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read version from version.py
version_path = Path(__file__).parent / "psrcdataportal" / "version.py"
version_info = {}
exec(version_path.read_text(encoding="utf-8"), version_info)

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="psrcdataportal",
    version=version_info["__version__"],
    author=version_info["__author__"],
    author_email=version_info["__email__"],
    description=version_info["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/psrc/psrcdataportal",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    include_package_data=True,
    package_data={
        "psrcdataportal": [
            "config/*.yaml",
            "config/*.yml",
        ],
    },
    entry_points={
        "console_scripts": [
            "psrc-export=psrcdataportal.cli:main",
        ],
    },
    keywords=[
        "gis",
        "arcgis",
        "data-portal",
        "spatial-data",
        "database",
        "export",
        "psrc",
        "transportation",
        "planning",
    ],
    project_urls={
        "Bug Reports": "https://github.com/psrc/psrcdataportal/issues",
        "Source": "https://github.com/psrc/psrcdataportal",
        "Documentation": "https://psrcdataportal.readthedocs.io/",
    },
)
