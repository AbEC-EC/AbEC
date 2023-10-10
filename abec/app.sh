#!/bin/sh

interface=1
pathAbec="./"
seed=42
i=1
pos=0
v=("$@")

if [ "$#" !=  "0" ]
then
    for arg in $v[@]
    do
        case $arg in
        "-i" )
            pos=$(($i+1))
            aee=(${v[$pos]})
            interface=$aee;;
        "-p" )
            pos=$(($i+1))
            aee=(${v[$pos]})
            pathAbec=$aee;;
        "-s" )
            pos=$(($i+1))
            aee=(${v[$pos]})
            seed=$aee;;
        esac
        i=$(($i+1))
    done
fi

# echo "Interface: $interface";
# echo "Path: $pathAbec";
# echo "Seed: $seed";

DIRECTORY="../docs/install/venv-abec/"

if [ ! -d "$DIRECTORY" ]; then
    echo "Please run the install.sh script in the previous dir with the command: \n"
    echo "source install.sh\n"
    echo "Obrigado!"
else
    source ../docs/install/venv-abec/bin/activate
    # echo $VIRTUAL_ENV
    # echo "Running the framework"
    # echo "./framework.py -i $interface -p $pathAbec"
    ./framework.py -i $interface -p $pathAbec
    deactivate
fi
