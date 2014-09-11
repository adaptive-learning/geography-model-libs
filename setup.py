# -*- coding: utf-8 -*-
from setuptools import setup

VERSION = '1.0.0'


setup(
    name='proso-model',
    version=VERSION,
    description='Models library for PROSO project',
    author='Jan Papousek',
    author_email='jan.papousek@gmail.com',
    namespace_packages = ['proso.models', 'proso'],
    packages=['proso.models', 'proso'],
    install_requires=['numpy>=1.8.1', 'scikit-learn>=0.15.0', 'matplotlib>=1.3.1', 'clint==0.3.7', 'scipy>=0.14.0'],
    license='Gnu GPL v3',
    url='https://github.com/proso/geography-model-libs/',
)
