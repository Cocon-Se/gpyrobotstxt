import setuptools

import gpyrobotstxt

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='gpyrobotstxt',
    version=gpyrobotstxt.__version__,
    author="CoconSe",
    author_email="blog@cocon.se",
    license='GPL v3',
    url="https://github.com/Cocon-Se/gpyrobotstxt",
    description="A pure Python port of Google's robots.txt parser and matcher.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "gpyrobotstxt"},
    packages=setuptools.find_packages(where="gpyrobotstxt"),
    install_requires=[
    ],
    python_requires='>=3.9',
    classifiers=[
      "Programming Language :: Python :: 3.9",
      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      "Operating System :: OS Independent",
    ],
)
