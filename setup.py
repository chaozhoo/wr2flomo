from setuptools import setup, find_packages

setup(
    name="wr2flomo",
    version="0.4.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt6>=6.4.0",
        "cryptography>=3.4.7",
        "keyring>=23.0.1",
        "requests>=2.26.0"
    ],
    entry_points={
        "console_scripts": [
            "wr2flomo=main:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.7",
)
