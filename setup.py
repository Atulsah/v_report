# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in v_report/__init__.py
from v_report import __version__ as version

setup(
	name='v_report',
	version=version,
	description='Report Generation',
	author='Frappe',
	author_email='atul.sah7@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
