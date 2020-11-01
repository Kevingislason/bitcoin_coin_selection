import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bitcoin_coin_selection",
    version="1.0.0",
    author="Kevin Gislason",
    author_email="kevingislason@gmail.com",
    description="Port of Bitcoin core coin selection logic to Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kevingislason/bitcoin_coin_selection",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries"
    ],
    python_requires='>=3.6',
)
