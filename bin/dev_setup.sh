#!/usr/bin/env bash

###########################################################
##### Create virtualenv for development.
# Virtaulenv needs to be installed for this to work.
# If you don't have virtualenv installed please visit
# https://pypi.python.org/pypi/virtualenv
# for instructions on installing virutalenv.
###########################################################

### Create the virtual environment.
# The virtualenv will attempt to make python 3
# environment. If the '-p python3' doesn't work, them most
# likely there is no python3 installed on local system.
python3 -m venv .venv

echo
echo "------------------------------------------------"
echo "- Virtual environment created in directory 'venv'"
echo "------------------------------------------------"

# Activate the virtual environment.
echo
echo "------------------------------------------------"
echo "----- Activating virtual env with command. -----"

source .venv/bin/activate

echo "------------------------------------------------"
echo


###########################################################
##### Install development related packages.
###########################################################
echo
echo "------------------------------------------------"
echo "------- Installing development packages --------"
echo "------------------------------------------------"
echo
python -m pip install --upgrade pip
pip install -r bin/dev_requirements.txt
pip install -r requirements.txt

###########################################################
##### Install the phenomena package in development mode.
###########################################################
echo
echo "------------------------------------------------"
echo "------ Setting up development environment ------"
echo "------------------------------------------------"

python -m build
