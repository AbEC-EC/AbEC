#!/bin/sh
if [[ "$(python3 -V)" =~ "Python 3" ]]
then 
    echo "Python 3 is already installed"
else
    echo "Python 3 is required in order to run the framework"
    echo "Installing python3 ..."
    sudo apt install python3.10 python3-pip
fi

echo "Setting the virtual enviroment up ..."
python3 -m venv docs/install/venv-abec
source ./docs/install/venv-abec/bin/activate
pip install -r ./docs/install/requirements.txt
echo "Done! now you can run the framework in the abec/ dir"
deactivate