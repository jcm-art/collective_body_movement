#!/usr/bin/env bash

echo "Running Setup Script for Collective Body."

# Install Python dependencies
if [[ "$(python3 -V)" =~ "Python 3" ]]
then
    echo "Verified Python 3 is already installed"
else
    brew install python3
fi

if [[ "$(virtualenv --version)" =~ "virtualenv" ]]
then
    echo "Verified virtualenv is already installed"
else
    pip install virtualenv
fi

# Create virtualenv
if [ -d "./cbenv" ]
then
    echo "Virtualenv already exists"
else
    echo "Creating virtualenv"
    virtualenv -p python3 cbenv
fi

source cbenv/bin/activate

# Install Python dependencies
pip3 install --upgrade pip
pip3 install numpy
pip3 install pandas
pip3 install matplotlib
pip3 install PyInstaller
pip3 install tk

# TODO - notebook install is broken
# Install notebook
# pip3 install --upgrade pyrsistent
# pip3 install jsonschema     
# pip3 install --upgrade jsonschema  
# pip3 install ipykernel    
# pip3 install jupyterlab

# conda create --name cb_condaenv 
# conda activate cb_condaenv  
# conda install -c conda-forge jupyterlab