import serial
import time

# ser = serial.Serial('/dev/ttyUSB0')  # open serial port
# print(ser.name)         # check which port was really used
# ser.close()
# with serial.Serial('/dev/ttyUSB0', 19200, timeout=1) as ser:
#     x = ser.read()  # read one byte
#     print(x)
#     s = ser.read(10)  # read up to ten bytes (timeout)
#     print(s)
#     line = ser.readline()  # read a '\n' terminated line
#     print(line)
# ser.close()  # close port

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.flushInput()
# cmd = input("Enter Command : ")
# ser.write(cmd.encode('ascii') + b'13' + b'10')
ser.write(b'start')
time.sleep(2)
ser.write(b'e')
#ser.reset_input_buffer()
#ser.reset_output_buffer()
#ser.flush()
# ser.write(b'Z')

time.sleep(2)
for _ in range(20):
    resp = ser.readline()
    print(resp)

ser.close()
