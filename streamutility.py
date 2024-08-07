import pathlib
import struct
import enum

class Padding(enum.Enum):
    pre_MSG_padding = "cd"
    post_MSG_padding = "cc"

def writeStrToLong(file, data):
    arr = bytearray([0,0,0,0])
    data = bytes(str(data), "utf-8")
    arr[:] = data
    file.write(arr)
def writeHexToLong(file, data):
    arr = bytearray([0,0,0,0])
    data = struct.pack('>l', data)
    arr[:] = data
    file.write(arr)
def writePadding(file, iterations, padding_string):
    # padding_string = bytes(padding_string, "utf-8")
    padding_byte = int(padding_string, 16)
    padding_byte = padding_byte.to_bytes(1, 'big')
    for i in range(0, iterations):
        file.write(padding_byte)
def writeShort():
    pass