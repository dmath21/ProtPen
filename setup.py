from setuptools import setup, find_packages

setup(
    name="protpen",
    version="0.1.0",
    description="ProtPen: Protein function prediction pipeline using sequence and structure-based tools",
    author="Diya Mathai",
    author_email="dtm3426@rit.edu",
    url="https://github.com/dmath21/ProtPen",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "cli-enrich=protpen.cli_enrich:main",
            "cli-merge=protpen.cli_merge:main",
            "cli-eggmap=protpen.cli_eggnog:main",
            "cli-foldseek=protpen.cli_foldseek:main",
            "cli-consolidate-foldseek=protpen.cli_consolidate_foldseek:main",
            "cli-download=protpen.cli_download:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
