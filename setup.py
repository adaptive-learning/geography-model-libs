# -*- coding: utf-8 -*-
from setuptools import setup

VERSION = '1.1.3'


setup(
    name='proso-geography-model',
    version=VERSION,
    description='Models library for PROSO Geography project',
    author='Jan Papousek',
    author_email='jan.papousek@gmail.com',
    namespace_packages = ['proso.geography', 'proso'],
    packages=['proso.geography', 'proso'],
    install_requires=['numpy==1.8.1', 'scikit-learn==0.15.0', 'matplotlib==1.3.1', 'clint==0.3.7', 'scipy==0.14.0'],
    license='Gnu GPL v3',
    url='https://github.com/proso/geography-model-libs/',
)
