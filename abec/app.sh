#!/bin/bash

interface=1
pathAbec="./"
seed=42
i=1
pos=0

while getopts ":i:p:s:" opt; do
  case $opt in
    i) interface="$OPTARG"
    ;;
    p) path="$OPTARG"
    ;;
    p) seed="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    exit 1
    ;;
  esac

  case $OPTARG in
    -*) echo "Option $opt needs a valid argument"
    exit 1
    ;;
  esac
done

#echo "Interface: $interface";
#echo "Path: $pathAbec";
#echo "Seed: $seed";

DIRECTORY="../docs/install/venv-abec/"

if [ ! -d "$DIRECTORY" ]; then
    echo "[Please run the install.sh script in the previous dir AbEC/]"
    echo "[use the command 'cd ..' to go there]"
    echo "[and run with the command './install.sh']"
    echo "[Obrigado!]"
else
    source ../docs/install/venv-abec/bin/activate
    # echo $VIRTUAL_ENV
    # echo "Running the framework"
    # echo "./framework.py -i $interface -p $pathAbec"
    ./framework.py -i $interface -p $path
    deactivate
fi
