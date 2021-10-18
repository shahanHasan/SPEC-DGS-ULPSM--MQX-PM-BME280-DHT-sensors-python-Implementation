import os
import signal
import time
import subprocess

filename = "/home/pi/Desktop/Module3/SPEC-sensor-python-Implementation/CSV_think_speak_Module.py"
bash_cmd = ["pgrep", "-f" , filename]
bash_cmd_re = ["reboot"]

result = subprocess.run(bash_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
pid = [int(x) for x in result.stdout.split()]
#print(f"{type(pid)} {pid}")
#print(f"{type(os.getpid())} {os.getpid()}")
[os.kill(int(p), signal.SIGINT) for p in pid]

time.sleep(20)

subprocess.run(bash_cmd_re, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)