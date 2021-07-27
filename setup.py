"""The setuptools setup file."""
from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

with open('VERSION') as version_file:
    version = version_file.read()

setup(
    name='phenomena',
    version=version,
    autho='Raul Gonzalez',
    author_email='mindbender@gmail.com',
    url='https//github.com/neoinsanity/cognate',
    license='Apache License 2.0',
    description='A perception by the senses or through immediate experience.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['phenomena', ],
    install_requires=[
        'cognate==1.0.0',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development',
    ],
)
