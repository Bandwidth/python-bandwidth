#!/usr/bin/env python
from setuptools import setup

setup(
    name='bandwidth_sdk',
    version='1.0.0-alpha',
    description='This client library is designed to support the Bandwidth '
                'API and the official Bandwidth SDK',
    author='Bandwidth',
    maintainer='Bandwidth',
    maintainer_email='classifieds-admin@bandwidth.com',
    url='',
    license='Apache',
    packages=["bandwidth_sdk"],
    long_description="Bandwidth Python API",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    install_requires=[
        'requests',
        'python-dateutil',
        'six'
    ],
)
