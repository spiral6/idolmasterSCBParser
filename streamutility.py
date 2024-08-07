import pathlib
import struct
import enum

class Padding(enum.Enum):
    pre_MSG_padding = "cd"
    post_MSG_padding = "cc"
    zero = "00"

def writeStrToLong(file, data):
    arr = bytearray([0,0,0,0])
    data = bytes(str(data), "ASCII")
    # data = struct.pack('>p', data)
    arr[:] = data
    file.write(arr)
def writeHexToLong(file, data):
    arr = bytearray([0,0,0,0])
    data = struct.pack('>l', data)
    arr[:] = data
    file.write(arr)
def writePadding(file, iterations, padding_enum: Padding):
    # padding_string = bytes(padding_string, "utf-8")
    padding_byte = int(padding_enum.value, 16)
    padding_byte = padding_byte.to_bytes(1, 'big')
    for i in range(0, iterations):
        file.write(padding_byte)
def writeHexToShort(file, data):
    arr = bytearray([0,0])
    data = struct.pack('>h', data)
    arr[:] = data
    file.write(arr)