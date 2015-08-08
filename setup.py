#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import store

deps = ['yowsup2', 'peewee']

setup(
    name='yowsup.layers.store',
    version=store.__version__,
    url='http://github.com/tgalal/yowlayer-store/',
    license='GPL-3+',
    author='Tarek Galal',
    tests_require=[],
    install_requires = deps,
    author_email='tare2.galal@gmail.com',
    description='A Storage layer for yowsup',
    packages= find_packages(),
    include_package_data=True,
    platforms='any',
    namespace_packages = ['yowsup.layers'],
    #test_suite='',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        #'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)