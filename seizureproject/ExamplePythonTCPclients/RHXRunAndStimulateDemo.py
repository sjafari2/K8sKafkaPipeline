# In order to run this example script successfully, the IntanRHX software should be started
# with a Stimulation/Recording Controller (or a synthetic Stimulation/Recording Controller);
# other controller types will not work with this script

# Through Network -> Remote TCP Control:

# Command Output should open a connection at 127.0.0.1, Port 5000.
# Status should read "Pending"

# Once this port is opened, this script can be run to use TCP commands to configure stimulation
# on channel A-010. Then, the controller will be run for 5 seconds, and every ~1 second a 
# TCP command to trigger stimulation will be sent.

import time, socket

def RunAndStimulateDemo():

    # Declare buffer size for reading from TCP command socket
    # This is the maximum number of bytes expected for 1 read. 1024 is plenty for a single text command
    COMMAND_BUFFER_SIZE = 1024 # Increase if many return commands are expected

    # Connect to TCP command server - default home IP address at port 5000
    print('Connecting to TCP command server...')
    scommand = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    scommand.connect(('127.0.0.1', 5000))

    # Query controller type from RHX software - throw an error and exit if controller type is not Stim
    scommand.sendall(b'get type')
    commandReturn = str(scommand.recv(COMMAND_BUFFER_SIZE), "utf-8")
    isStim = commandReturn == "Return: Type ControllerStimRecordUSB2"
    if not isStim:
        raise Exception('This example script should only be used with a Stimulation/Recording Controller')

    # Query runmode from RHX software
    scommand.sendall(b'get runmode')
    commandReturn = str(scommand.recv(COMMAND_BUFFER_SIZE), "utf-8")
    isStopped = commandReturn == "Return: RunMode Stop"

    # If controller is running, stop it
    if not isStopped:
        scommand.sendall(b'set runmode stop')
        time.sleep(0.1)

    # Send commands to configure some stimulation parameters on channel A-010, and execute UploadStimParameters for that channel
    scommand.sendall(b'set a-010.stimenabled true')
    time.sleep(0.1)
    scommand.sendall(b'set a-010.source keypressf1')
    time.sleep(0.1)
    scommand.sendall(b'set a-010.firstphaseamplitudemicroamps 10')
    time.sleep(0.1)
    scommand.sendall(b'set a-010.firstphasedurationmicroseconds 500')
    time.sleep(0.1)
    scommand.sendall(b'execute uploadstimparameters a-010')
    time.sleep(1)

    # Send command to set board running
    scommand.sendall(b'set runmode run')

    # Every second for 5 seconds, execute a ManualStimTriggerPulse command
    print("Acquiring data, and stimulating every second")
    for elapsedSeconds in range(5):
        time.sleep(1)
        scommand.sendall(b'execute manualstimtriggerpulse f1')
    time.sleep(0.1)

    # Send command to RHX software to stop recording
    scommand.sendall(b'set runmode stop')
    time.sleep(0.1)

    # Close TCP socket
    scommand.close()

RunAndStimulateDemo()