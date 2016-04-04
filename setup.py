"""The setuptools setup file."""
from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

with open('VERSION') as version_file:
    version = version_file.read().strip()

requires = [
    'cognate==0.0.4',
    'decorator==4.0.9',
    'gevent==1.1.0',
    'ontic==0.0.4',
    'pyzmq==15.2.0',
]

setup(
    name='phenomena',
    version=version,
    author='Raul Gonzalez',
    author_email='mindbender@gmail.com',
    url='https://github.com/neoinsanity/phenomena',
    license='Apache License 2.0',
    description='Being of Beings',
    long_description=long_description,
    packages=[
        'phenomena',
        'phenomena.connection_types',
    ],
    install_requires=requires,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
    ]
)

