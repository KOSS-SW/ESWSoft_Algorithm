import serial
import sys

print(sys.argv[1])
serial_ = serial.Serial('/dev/ttyS0', 4800, timeout=0.01)
serial_.flush() # serial cls


serial_.write(serial.to_bytes([sys.argv[1]]))
