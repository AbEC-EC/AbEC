#!/bin/sh

sudo apt install python3.10 python3-pip
python3 -m venv abec/aux/install/venv-abec
source ./abec/aux/install/venv-abec/bin/activate
pip install -r ./abec/aux/install/requirements.txt
deactivate
