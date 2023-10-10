#!/bin/sh
if [[ "$(python3 -V)" =~ "Python 3" ]]
then 
    echo "Python 3 is already installed"
else
    echo "Installing python3 ..."
    sudo apt install python3.10 python3-pip
echo "Setting the virtual enviroment up ..."
python3 -m venv docs/install/venv-abec
source ./docs/install/venv-abec/bin/activate
pip install -r ./docs/install/requirements.txt
deactivate