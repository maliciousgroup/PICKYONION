#!/usr/bin/env python2

from setuptools import setup

setup(
  name='pickyonion',
  version='0.0.1',
  description='A red team base module for tor operations',
  url='http://github.com/blackhatstoday/pickyonion',
  author='Blackhats Today',
  author_email='info@blackhats.today',
  license='FU',
  py_modules=['pickyonion'],
  install_requires=[
    'PySocks>=1.5.7',
    'requests>=2.11.0',
    'stem>=1.4.0'
  ],
  zip_safe=False)
