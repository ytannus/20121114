from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in contracts/__init__.py
from contracts import __version__ as version

setup(
	name="contracts",
	version=version,
	description="Contract Management System",
	author="Your Company",
	author_email="contact@yourcompany.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
