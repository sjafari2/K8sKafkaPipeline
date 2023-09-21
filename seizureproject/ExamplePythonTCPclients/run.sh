#!/bin/sh
#Make Qt platform plugin "xcb" able to connect to the display on Windows Subsystem for Linux (WSL).
#export DISPLAY=10.0.0.157:0.0

## Add Qt to the library path
#export LD_LIBRARY_PATH=/usr/lib64/qt5/plugins/platforms/libqxcb.so
#:$LD_LIBRARY_PATH


#set -x # Print each command your shell script is executing.

## Kill any intanRHX process if running ##
#./kill.sh IntanRHX

#echo Running IntanRHX
#cd /usr/local/IntanRHX
#./IntanRHX &


#cd /home/neurosci/RHX_TCP/TCP/Example\ Python\ TCP\ clients
#echo "Current directory: $(pwd)" # Verify the current directory again.

rm *.txt

echo "Running RHX Read Wave from Data"
python3 RHXReadWaveformData.py > readwave_output.txt 2> readwave_error.txt # Log output and errors to files.
echo "Exit status of RHX Read Wave from Data: $?" # Check exit status of the Python script.

#echo "Running RHX Run and Stimulate"
#python3 RHXRunAndStimulateDemo.py > runstimulate_output.txt 2> runstimulate_error.txt # Log output and errors to files.
#echo "Exit status of RHX Run and Stimulate: $?" # Check exit status of the Python script.

echo "Running RHX Save to Disk"
python3 RHXSaveToDiskPythonDemo.py > savedisk_output.txt 2> savedisk_error.txt # Log output and errors to files.
#echo "Exit status of RHX Save to Disk: $?" # Check exit status of the Python script.

#set +x # Disable printing each command your shell script is executing.
