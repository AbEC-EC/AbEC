#!/bin/bash

# Function to display the confirmation prompt
function confirm() {
    while true; do
        read -p "$1" yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            [Cc]* ) exit;;
            * ) echo "Please answer y (yes) or n (no).";;
        esac
    done
}

text="[Do you want to install the AbCD framework?][y/n]: "
if confirm "$text"; then
    echo
    echo "[Checking the requirements]:"
    sleep 1.5
    if [[ "$(python3 -V)" =~ "Python 3" ]]
    then
        echo "-- [Python 3 is already installed]"
    else
        echo "-- [Python 3 is required to use the framework. It is gonna be installed]"
        text="-- [Do you want to install it?][y/n]: "
        if confirm "$text"; then
            echo "---- [Installing python3]:"
            sleep 1.5
            sudo apt install python3.10 python3-pip
            echo "------ [Python3 installed!]"
        else
            echo "-- [Puxa :(]"
        fi
    fi

    echo
    echo "[Setting the virtual environment up]:"
    python3 -m venv docs/install/venv-abec
    echo "-- [Environment created]"
    source ./docs/install/venv-abec/bin/activate
    echo "-- [Changed the source]:"
    echo "---- [$VIRTUAL_ENV]"
    echo "-- [Installing python dependencies on the virtual environment]:"
    sleep 1.5
    pip install -r ./docs/install/requirements.txt
    echo "---- [Dependencies installed!]"
    echo
    echo "[Done! now you can run the framework in the abec/ dir]"
    echo "[use the command 'cd abec' to go there]"
    echo "[and run with the command './app.sh' (or './app.sh -i 0' to non graphical interface)]"
    echo "[Obrigado!]"
    # deactivate
else
        echo "[Puxa :(]"
fi
