import codecs
import os.path
from setuptools import setup, find_packages

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='gpyrobotstxt',
    keywords='gpyrobotstxt',
    version=get_version("gpyrobotstxt/__init__.py"),
    author="CoconSe",
    author_email="blog@cocon.se",
    license='GPL v3',
    url="https://github.com/Cocon-Se/gpyrobotstxt",
    description="A pure Python port of Google's robots.txt parser and matcher.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    packages=find_packages(include=['gpyrobotstxt']),
    install_requires=[
    ],
    python_requires='>=3.9',
    classifiers=[
      "Programming Language :: Python :: 3.9",
      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      "Operating System :: OS Independent",
    ],
)
