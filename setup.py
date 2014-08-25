"""The setuptools setup file."""
from setuptools import setup

with open('README.txt') as file:
    long_description = file.read()

requires = [
    'ontic==0.0.3a',
    'gevent==1.0.1',
    'pyzmq==14.3.1',
    'cognate']

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
    install_requires=requires,
    include_package_data = True,
)

