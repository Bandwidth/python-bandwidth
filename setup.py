#!/usr/bin/env python
from setuptools import setup

setup(
    name='bandwith_sdk',
    version='1.0.0-alpha',
    description='This client library is designed to support the Bandwith '
                'API and the official Bandwith SDK',
    author='Bandwith',
    maintainer='Bandwith',
    maintainer_email='classifieds-admin@bandwidth.com',
    url='',
    license='Apache',
    packages=["bandwith_sdk"],
    long_description="Bandwidth Python API",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    install_requires=[
        'requests',
    ],
)
