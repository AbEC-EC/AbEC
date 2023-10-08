#!/bin/sh

sudo apt install python3.10 python3-pip
python3 -m venv docs/install/venv-abec
source ./docs/install/venv-abec/bin/activate
pip install -r ./docs/install/requirements.txt
deactivate
