#!/usr/bin/env zsh

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
pip install pandas
