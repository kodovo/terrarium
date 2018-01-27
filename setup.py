#!/usr/bin/env python3

# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='terrarium',
    version='0.0.1',
    description='Terrarium control for Raspberry Pi',
    long_description=long_description,
    url='https://github.com/kodovo/terrarium',
    author='Pekko Metsä',
    author_email='pjmetsa@gmail.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Other Audience',
        'Topic :: Home Automation',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        ],
    keywords='terrarium automation relay lights heat humidity',
    install_requires=['RPi.GPIO'],
    package_dir={'':'src'}
)
