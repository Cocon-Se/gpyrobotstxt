import setuptools

import pyrobotstxt

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyrobotstxt',
    version=pyrobotstxt.__version__,
    author="Cocon-Se",
    author_email="blog@cocon.se",
    license='Apache',
    url="https://github.com/Cocon-Se/pyrobotstxt",
    description="A pure Python port of Google's robots.txt parser and matcher.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "pyrobotstxt"},
    packages=setuptools.find_packages(where="pyrobotstxt"),
    install_requires=[
    ],
    python_requires='>=3.10',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
)
