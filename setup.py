from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='gpyrobotstxt',
    keywords='gpyrobotstxt',
    version="1.0.0",
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
