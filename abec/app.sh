#!/bin/sh


DIRECTORY="../docs/install/venv-abec/"

if [ ! -d "$DIRECTORY" ]; then
    echo "Please run the install.sh script in the previous dir with the command: \n"
    echo "source install.sh\n"
    echo "Obrigado!"
else
    source ../docs/install/venv-abec/bin/activate
    # echo $VIRTUAL_ENV
    echo "Running the framework"
    ./abec.py
    deactivate
fi
