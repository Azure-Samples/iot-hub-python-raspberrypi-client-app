#!/bin/bash
if [ $# -eq 2 ]
then
    if ! [[ $1 == "--python-version" || $1 == "-p" ]]; then
        echo -e "Parameter is not right\nUsage: setup.sh [--python-version|-p] [2.7|3.4|3.5]"
        exit
    fi

    if ! [[ $2 == 2.7 || $2 == 3.4 || $2 == 3.5 ]]; then
        echo -e "Python version is not right\n You can use python version 2.7, 3.4 and 3.5\nUsage: setup.sh [--python-version|-p] [2.7|3.4|3.5]"
        exit
    fi
    INPUT_PYTHON_VERSION=$2
elif [ $# -eq 0 ]
then
    INPUT_PYTHON_VERSION="0"
else
    echo -e "Parameter is not right\nUsage: setup.sh [--python-version|-p] [2.7|3.4|3.5]"
    exit
fi
CMAKE_LEAST="2.8.12"
GCC_LEAST="4.4.7"
vercomp() {
    if [[ $1 == $2 ]]
    then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    # fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++))
    do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++))
    do
        if [[ -z ${ver2[i]} ]]
        then
            # fill empty fields in ver2 with zeros
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]}))
        then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]}))
        then
            return 2
        fi
    done
    return 0
}
checkpython() {
    PYTHON2_VER=`python --version 2>&1 | cut -d" " -f2`
    PYTHON3_VER=`python3 --version 2>&1 | cut -d" " -f2`
    if [[ $1 == 0 ]]
    then
        echo "python version not specified,auto detecting..."
        if [[ $PYTHON2_VER == 2.7* ]]
        then
            echo "Use python $PYTHON2_VER"
            PYTHON_VERSION="2.7"
        elif [[ $PYTHON3_VER == 3.4* ]]
        then
            echo "use python $PYTHON3_VER"
            PYTHON_VERSION="3.4"
        elif [[ $PYTHON3_VER == 3.5* ]]
        then
            echo "use python $PYTHON3_VER"
            PYTHON_VERSION="3.5"
        fi
    elif [[ $1 == 2.7 ]]
    then
        if [[ $PYTHON2_VER == 2* ]]
        then
            echo "use python $PYTHON2_VER"
	    PYTHON_VERSION="2.7"
        else
            echo "Python 2.7 not found"
            exit 1
        fi
    elif [[ $1 == 3.4 ]]
    then
        if [[ $PYTHON3_VER == 3.4* ]]
        then
            echo "use python $PYTHON3_VER"
	    PYTHON_VERSION="3.4"
        else
            echo "Python 3.4 not found"
            exit 1
        fi
    elif [[ $1 == 3.5 ]]
    then
        if [[ $PYTHON3_VER == 3.5* ]]
        then
            echo "use python $PYTHON3_VER"
	    PYTHON_VERSION="3.5"
        else
            echo "Python 3.5 not found"
            exit 1
        fi
    else
        echo "Invalid python version specified"
        exit 1
    fi
}
GCC_VER=`gcc --version | head -n1 | cut -d" " -f4`
CMAKE_VER=`cmake --version | head -n1 | cut -d" " -f3`
vercomp $GCC_VER $GCC_LEAST
if [ $? -eq 2 ]
then
    echo "gcc version too low (current:$GCC_VER,require:$GCC_LEAST)"
else
    echo "gcc version check pass (current:$GCC_VER,require:$GCC_LEAST)"
fi
vercomp $CMAKE_VER $CMAKE_LEAST
if [ $? -eq 2 ]
then
    echo "cmake version too low (current:$CMAKE_VER,require:$CMAKE_LEAST)"
else
    echo "cmake version check pass (current:$CMAKE_VER,require:$CMAKE_LEAST)"
fi
checkpython $INPUT_PYTHON_VERSION

sudo apt-get update

sudo apt-get install -y cmake build-essential curl libcurl4-openssl-dev libssl-dev uuid-dev python-dev python-smbus

if [[ $PYTHON_VERSION == 2.7 ]]; then
    sudo apt-get install -y python-pip
else
    sudo apt-get install -y python3-pip
fi

git clone https://github.com/Azure/azure-iot-sdk-python.git --recursive
cd azure-iot-sdk-python/build_all/linux
./setup.sh --python-version $PYTHON_VERSION
./build.sh --build-python $PYTHON_VERSION
cd ../../device/samples
cp iothub_client.so ../../../iothub_client.so

if [[ $PYTHON_VERSION == 2.7 ]]; then
    sudo pip install RPi.GPIO
    sudo pip install applicationinsights
else
    sudo pip3 install RPi.GPIO
    sudo pip3 install applicationinsights
fi

git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO

if [[ $PYTHON_VERSION == 2.7 ]]; then
    sudo python setup.py install
else
    sudo python3 setup.py install
fi

cd ..

