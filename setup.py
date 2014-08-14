"""The setuptools setup file."""
from setuptools import setup

with open('README.txt') as file:
    long_description = file.read()

setup(
    name='phenomena',
    version='0.0.0',
    author='Raul Gonzalez',
    author_email='mindbender@gmail.com',
    url='https://github.com/neoinsanity/phenomena',
    license='Apache License 2.0',
    description='From the same root',
    long_description=long_description,
    packages=['phenomena',],
    install_requires=[],
    include_package_data = True,
)

