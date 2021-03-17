import paramiko
import os
import time
import atexit
"""
The aim of this file is to provide simple methods to send SSH requests in Emulated Shell mode 
"""

#Deprecated
def send_command(hostname,command,username='Admin',password='12345678',buffer_time=0):
    """
    Send a single command using SSH Emulated Shell mode
    inputs:
        hostname: Device IP address
        command (str): Command to send
        buffer_time : Unused by default. Permit using a sleeping time before retrieving response from shell
    outputs:
        s.splitlines() : Standard output of the Shell as a list of lines
    """
    #SSH client Initialization
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    #Starting Emulated shell
    chan = ssh.invoke_shell()
    #Sending command and Pressing "Enter"
    chan.sendall(command+'\n')
    if buffer_time!=0: 
        time.sleep(buffer_time)    
        s=chan.recv(4096).decode("utf-8")
    else:
        s=chan.recv(4096).decode("utf-8")
        while len(s.splitlines())<4:
            s=s+chan.recv(4096).decode("utf-8")
        while s.splitlines()[-1] not in s.splitlines()[2]:
            s=s+chan.recv(4096).decode("utf-8")
    ssh.close()
    return s.splitlines()


def send_list_commands(hostname,commands,stop='',username='Admin',password='12345678',buffer_time=0):
    """
    Send a list of commands using SSH Emulated Shell mode
    inputs:
        hostname: Device IP address
        command (list(str)) : Commands to send (sequential)
        stop (str) : Permit declaring a trigger value to detect the end of the command execution
                    For NEC VR, I would suggest to use the hostname
        buffer_time : Unused by default. Permit using a sleeping time before retrieving response from shell


        This method will sequentially send those commands. For each command, if no buffer_time is set
        it will wait for a specific value called "stop". This is required because the shell emulation 
        isn't synchronous, which means that while receiving the SSH response, you can't tell
        if the response is complete. 
        
        For NEC VR use, I would suggest to the hostname as a "stop" value because it is the only immuable
        value that should appears at the end of the command execution

    outputs:
        s.splitlines() : Standard output of the Shell as a list of lines
    """
    #SSH client Initialization
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    #Starting Emulated shell
    chan = ssh.invoke_shell()
    if stop=='':
        s=chan.recv(4096).decode("utf-8")
        while len(s.splitlines()[-1].split('@'))==1:
            s=s+chan.recv(4096).decode("utf-8")
        stop=s.splitlines()[-1].split('@')[0]
    result_list = list()
    time.sleep(1)
    config_if=False
    config=False
    for command in commands:
        print(command)
        if 'interface' in command : config_if=True
        if 'config' == command : config=True
        s=''
        chan.sendall(command+'\n')
        if buffer_time!=0:
            time.sleep(buffer_time)    
            s=s+chan.recv(4096).decode("utf-8")
        else:
            s=s+chan.recv(4096).decode("utf-8")
            if config_if or config:
                end_state=''
                if config and not config_if: end_state=stop+'@1(config)'
                else: end_state=stop+'@1(config-if)'
                while len([line for line in s.splitlines() if end_state in line])<2:
                    s=s+chan.recv(4096).decode("utf-8")
                    time.sleep(1)
                    chan.sendall('\n')
            else:
                while stop not in s.splitlines()[-1]:
                    s=s+chan.recv(4096).decode("utf-8")
                    chan.sendall('\n')

        result_list.append(str(s))
    ssh.close()
    return result_list




def ssh_close():
    """
    Processed method while exiting the Python execution
    This prevents SSH sessions from remaining open if the execution is forced to be closed.
    """
    for vars in dir():
        if vars.startswith("ssh"):
            print(vars.close())
            print('SSH session closed')

atexit.register(ssh_close)

