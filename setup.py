# -*- coding: utf-8 -*-
from setuptools import setup

VERSION = '0.9.10'


setup(
    name='proso-geography-model',
    version=VERSION,
    description='Models library for PROSO Geography project',
    author='Jan Papousek',
    author_email='jan.papousek@gmail.com',
    namespace_packages = ['proso.geography', 'proso'],
    packages=['proso.geography', 'proso'],
    license='Gnu GPL v3',
    url='https://github.com/proso/geography-model-libs/',
)
