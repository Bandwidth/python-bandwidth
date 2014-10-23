#!/usr/bin/env python
from setuptools import setup

setup(
    name='bandwidth_sdk',
    version='1.0.2-stable',
    description='This client library is designed to support the Bandwidth '
                'API and the official Bandwidth SDK',
    author='bandwidth',
    maintainer='bandwidth',
    maintainer_email='classifieds-admin@bandwidth.com',
    url='https://github.com/bandwidthcom/python-bandwidth',
    license='Apache',
    packages=["bandwidth_sdk"],
    long_description="Bandwidth Python API",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    install_requires=[
        'requests',
        'python-dateutil',
        'six'
    ],
)
