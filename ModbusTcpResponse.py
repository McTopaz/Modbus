'''
Creates a Modbus TCP response from a single object.

Input:
    * TID: The transmission identifier.
    * Data type: The data type, as a character, to parse the value as. See data types.
    * Package: The entire package sent from the Modbus slave.
    Example: .\ModbusTcpReponse <TID> <data type> <package>.
             .\ModbusTcpReponse 0 i 000000000007010304XXXXXXXX.
    
Output:
    * Positive response: [ACK] <value>.
    * Negative response: [NAK]: <error code>.
    * Invalid response: Error message.
    
Data types:
	* ? = bool,		represented as unsigned INT8
	* b = INT8,		signed INT8
	' B = UINT8,	unsigned INT8
	* h = INT16,	signed INT16
	* H = UINT16,	unsigned INT16
	* i = INT32,	signed INT32
	* I = UINT32,	unsigned INT32
	* q = INT64,	signed INT64
	* Q = UINT64,	unsigned INT64
	* f = REAL32,	32-bits real number (float)
	* d = REAL64,	64-bits real number (double)
	* s# = string,	with # amount of characters

Positive response format:
[TID TID] [PID PID] [LEN LEN] ADR FUNC COUNT [    DATA   ]
  00  00    00  00    00  07   00   03    04  01 00 00 90

Negative response format:
[TID TID] [PID PID] [LEN LEN] ADR FUNC ERROR
  00  00    00  00    00  03   00   83    02 
'''

import sys
import struct

# Check if a data type is valid.
def ValidDataType(dataType):
    # Create a list of all data types except the string types.
    dataTypes = ["?", "b", "B", "h", "H", "i", "I", "q", "Q", "f", "d"]
    
    # Check if the data type is any of the none-string data types.
    if dataType in dataTypes:
        return True
    
    # Check if data type is a string.
    elif 's' in dataType:
        characters = dataType[1:]   # Get characters after 's'.
        # Check if characters after 's' is a digit.
        if characters.isdigit() == False:
            print("Error: String data type's length is invalid.")
            sys.exit()
        value = int(characters)	# Get actual amount of characters.
        # Check if the string's length is 0 or > 0xFF amount of characters.
        if value == 0x00:
            print("Too short string.")
            sys.exit()
        elif value > 0xFF:
            print("Error: Too long string.")
            sys.exit()
        else:
            return True
    else:
        return False

# Parse the package into a byte-array.
def ParsePackageToData(package):
    data = []

    # Iterate over every other characters.
    for start in range(0, len(package), 2):

        # Try to convert hex string to int.
        try:
            temp = int(package[start:start + 2], 16)
            data.append(temp)
        except:
            print("Error: '%s' contains a none hexadecimal number."%(package[1]))
            sys.exit()
     
    return data

# Get how many bytes there is for a specific data type.
def DataTypeByteCount(dataType):
    if dataType == '?':		# BOOL.
        return 1
    elif dataType == 'b':	# INT8.
        return 1
    elif dataType == 'B':	# UINT8.
        return 1
    elif dataType == 'h':	# INT16.
        return 2
    elif dataType == 'H':	# UINT16.
        return 2
    elif dataType == 'i':	# INT32.
        return 4
    elif dataType == 'I':	# UINT32.
        return 4
    elif dataType == 'q':	# INT64.
        return 8
    elif dataType == 'Q':	# UINT64.
        return 8
    elif dataType == 'f':	# REAL32.
        return 4
    elif dataType == 'd':	# REAL64.
        return 8
	# String data type.
    elif 's' in dataType:
        characters = dataType[1:]	# Get characters after 's'.
        value = int(characters)	# Get actual amount of characters.

        if value == 1:	# s1
            return 1
        else:
            # s2 to s255.
            count = 0
            if value % 2 == 0:
                count = value / 2 
            else:
                count = (value / 2) + 1
            return count

# Get value based on data type.
def ValueFromDataType(dataType, data):
    if dataType == '?':		# BOOL.
        return data[0] > 0x00
    elif dataType == 'b':	# INT8.
        return int.from_bytes(data, byteorder='big', signed=True)
    elif dataType == 'B':	# UINT8.
        return int.from_bytes(data, byteorder='big', signed=False)
    elif dataType == 'h':	# INT16.
        key = struct.pack('B' * len(data), *data)
        return struct.unpack('>h', key)
    elif dataType == 'H':	# UINT16.
        return int.from_bytes(data, byteorder='big', signed=False)
    elif dataType == 'i':	# INT32.
        return int.from_bytes(data, byteorder='big', signed=True)
    elif dataType == 'I':	# UINT32.
        return int.from_bytes(data, byteorder='big', signed=False)
    elif dataType == 'q':	# INT64.
        return int.from_bytes(data, byteorder='big', signed=True)
    elif dataType == 'Q':	# UINT64.
        return int.from_bytes(data, byteorder='big', signed=False)
    elif dataType == 'f':	# REAL32.
        key = struct.pack('B' * len(data), *data)
        return struct.unpack('f', key)
    elif dataType == 'd':	# REAL64.
        key = struct.pack('B' * len(data), *data)
        return struct.unpack('d', key)
        
	# String data type.
    elif 's' in dataType:
        characters = dataType[1:]	# Get characters after 's'.
        value = int(characters)	# Get actual amount of characters.

        if value == 1:	# s1
            return 1
        else:
            # s2 to s255.
            count = 0
            if value % 2 == 0:
                count = value / 2 
            else:
                count = (value / 2) + 1
            return count
        
# Check arguments.
if len(sys.argv) < 4:
    print("Error: Too few arguments.")
    sys.exit()

# Get arguments.
tid = sys.argv[1]       # Get the TID.
dataType = sys.argv[2]  # Get the data type.

# Check TID.
if tid.isdigit() == False or int(tid) > 0xFFFF:
    print("Error: Invalid TID.")
    sys.exit()
tid = int(tid, 16)  # Convert to int.
    
# Check data type.
if ValidDataType(dataType) == False:
    print("Error: Invalid data type.")
    sys.exit()

# Get response from arguments.
response = ParsePackageToData(sys.argv[3])
print(response)
    
# Check response.
if len(response) < 9:
    print("Invalid response length.")
    sys.exit()

TID = (256*response[0]) + response[1]
PID = (256*response[2]) + response[3]
LEN = (256*response[4]) + response[5]
ADR = response[6]
FUNC = response[7]

#print("TID: %s"%(TID))
#print("PID: %s"%(PID))
#print("LEN: %s"%(LEN))
#print("ADR: %s"%(ADR))
#print("FUNC: %s"%(FUNC))

# Check if TID in response is same as argument.
if tid != TID:
    print("Error: TID in response is not equal to TID in request.")
    sys.exit()
 
# Get if response is ACK or NAK.
isACK = (FUNC & 0x80) < 0x80
isNAK = (FUNC & 0x80) > 0x80

# Parse positive response.
if isACK:
    
    bytes = DataTypeByteCount(dataType)
    #print(len(response[6:]))
    #print(len(response[9:]))
    
    # Check if the LEN's value is equal to total bytes of (ADR+FUCN+COUNT+DATA).
    if len(response[6:]) != LEN:
        print("Error: Response's LEN is not equal to bytes in ADR, FUNC, COUNT and DATA.")
        sys.exit()
    # Check if the COUNT value is equal to total bytes of DATA.
    elif len(response[9:]) != bytes:
        print("Error: Response's COUNT is not equal to bytes in DATA")
        sys.exit()
    
    value = ValueFromDataType(dataType, response[9:])
    print("[ACK] %s"%(value))
    
# Parse negative response.
elif isNAk:
    pass
    
# Unknown response.
else:
    print("Error: Unknown response.")
    sys.exit()
