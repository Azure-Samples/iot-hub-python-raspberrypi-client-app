# IoT Hub Raspberry Pi 3 Client application

> This repo contains the source code to help you get started with Azure IoT using the Microsoft IoT Pack for Raspberry Pi 3 Starter Kit. You will find the [full tutorial on Docs.microsoft.com](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-raspberry-pi-kit-c-get-started).

This repo contains a python application that runs on Raspberry Pi 3 with a BME280 temperature&humidity sensor, and then sends these data to your IoT hub. At the same time, this application receives Cloud-to-Device messages from your IoT hub, and takes actions according to the C2D command. 

## Step 1: Set up your Pi
### Enable SSH on your Pi
Follow [this page](https://www.raspberrypi.org/documentation/remote-access/ssh/) to enable SSH on your Pi.

### Enable SPI and I2C on your Pi
Follow [this page](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to enable SPI on your Pi

## Step 2: Connect your sensor with your Pi
### Connect with a physical BEM280 sensor and LED
You can follow the image to connect your BME280 and an LED with your Raspberry Pi 3.

![BME280](https://docs.microsoft.com/en-us/azure/iot-hub/media/iot-hub-raspberry-pi-kit-c-get-started/3_raspberry-pi-sensor-connection.png)

### DON'T HAVE A PHYSICAL BME280?
You can use the application to simulate temperature&humidity data and send to your IoT hub.
1. Open the `config.py` file.
2. Change the `SIMULATED_DATA` value from `False` to `True`.


## Step 3: Build Azure IoT SDK for Python
### Installs needed to compile the SDKs for Python from source code
Because the Azure IoT SDKs for Python are wrappers on top of the [SDKs for C][azure-iot-sdk-c], you will need to compile the C libraries if you want or need to generate the Python libraries from source code.
You will notice that the C SDKs are brought in as submodules to the current repository.
In order to setup your development environment to build the C binaries make sure all dependencies are installed before building the SDK. 

- You can use apt-get to install the right packages:
  ```
  sudo apt-get update
  sudo apt-get install -y git cmake build-essential curl libcurl4-openssl-dev libssl-dev uuid-dev
  ```

- Verify that CMake is at least version **2.8.12**:
  ```
  cmake --version
  ```

- Verify that gcc is at least version **4.4.7**:
  ```
  gcc --version
  ```

### Compile the Python modules
The Python iothub_client and iothub_service_client modules support python versions 2.7.x, 3.4.x or 3.5.x. Know the appropriate version you would like to build the library with for the following instructions.

1. Clone the Azure IoT SDK for Python: https://github.com/Azure/azure-iot-sdk-python.git --recursive
2. Ensure that the desired Python version (2.7.x, 3.4 or 3.5.x) is installed and active. Run `python --version` or `python3 --version` at the command line to check the version.
3. Open a shell and navigate to the folder **build_all/linux** in your local copy of the repository.
3. Run the `./setup.sh` script to install the prerequisite packages and the dependent libraries.
    * Setup will default to python 2.7
    * To setup dependencies for python 3.4 or 3.5, run `./setup.sh --python-version 3.4` or `./setup.sh --python-version 3.5` respectively
4. Run the `./build.sh` script.
    * Build will default to python 2.7
    * To build with python 3.4 or 3.5, run `./build.sh --build-python 3.4` or `./build.sh --build-python 3.5` respectively 
5. After a successful build, the `iothub_client.so` Python extension module is copied to the [**device/samples**][device-samples] and [**service/samples**][service-samples] folders. **Please notice that the `iothub_client.so` will be used in this client application**. 

###Known build issues: 

1.) On building the Python client library (`iothub_client.so`) on Linux devices that have less than **1GB** RAM, you may see build getting **stuck** at **98%** while building `iothub_client_python.cpp` as shown below

``[ 98%] Building CXX object python/src/CMakeFiles/iothub_client_python.dir/iothub_client_python.cpp.o``

If you run into this issue, check the **memory consumption** of the device using `free -m command` in another terminal window during that time. If you are running out of memory while compiling iothub_client_python.cpp file, you may have to temporarily increase the **swap space** to get more available memory to successfully build the Python client side device SDK library.

## Step 4: Run your client application

1. Clone the client application to local:

   ```
   git clone https://github.com/Azure-Samples/iot-hub-python-raspberrypi-client-app.git
   
   cd ./iot-hub-python-raspberrypi-client-app
   ```

2. Install GPIO library:
   ```
   sudo pip install RPi.GPIO
   ```

3. Copy the `iothub_client.so` Python extension module generated in **Step 3** to this client application folder.

4. Run the client application with root privilege, and you also need provide your Azure IoT hub device connection string, note your connection should be quoted in the command:
   ```
   sudo python app.py '<your Azure IoT hub device connection string>'
   ```

If the application works normally, then you will see the screen like this:

![](./imgs/success.png)

