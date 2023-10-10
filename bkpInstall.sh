#!/bin/sh

curl https://pyenv.run | bash
pyenv install 3.10.0
pyenv shell 3.10
python -m venv docs/install/venv-abec
source ./docs/install/venv-abec/bin/activate
pip install -r ./docs/install/requirements.txt
deactivate
