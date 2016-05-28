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
    data = b""

    # Iterate over every other characters.
    for i in range(int(len(package)/2)):

        # Try to convert hex string to int.
        try:
            temp = int(package[2*i:2*i+2], 16)
            data += struct.pack("B",temp)
        except:
            print("Error: '%s' contains a none hexadecimal number."%(package[i]))
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
        
        # Round up uneven length strings: s3 = s4.
        if value % 2 != 0:
            value = value + 1
            
        value *= 2  # Double the byte count since Modbus use two bytes per register.
        return value

# Get value based on data type.
def ValueFromDataType(dataType, data):
    if dataType == '?':		# BOOL.
        return data[0] > 0x00
    elif dataType == 'b':	# INT8.
        return struct.unpack('>b', data)
    elif dataType == 'B':	# UINT8.
        return struct.unpack('>B', data)
    elif dataType == 'h':	# INT16.
        return struct.unpack('>h', data)
    elif dataType == 'H':	# UINT16.
        return struct.unpack('>H', data)
    elif dataType == 'i':	# INT32.
        return struct.unpack('>i', data)
    elif dataType == 'I':	# UINT32.
        return struct.unpack('>I', data)
    elif dataType == 'q':	# INT64.
        return struct.unpack('>q', data)
    elif dataType == 'Q':	# UINT64.
        return struct.unpack('>Q', data)
    elif dataType == 'f':	# REAL32.
        return struct.unpack('f', data)
    elif dataType == 'd':	# REAL64.
        return struct.unpack('d', data)
        
	# String data type.
    elif 's' in dataType:
        return "".join(chr(i) for i in data)

# Look up an error message based on the error code.        
def LookupErrorMessage(errorCode):
    if errorCode == 0x01:
        return "Illegal function.";
    elif errorCode == 0x02:
        return "Illegal data address.";
    elif errorCode == 0x03:
        return "Illegal data value.";
    elif errorCode == 0x04:
        return "Slave device failure.";
    elif errorCode == 0x05:
        return "Acknowledge.";
    elif errorCode == 0x06:
        return "Slave device busy.";
    elif errorCode == 0x07:
        return "Negative acknowledge.";
    elif errorCode == 0x08:
        return "Memory parity error.";
    elif errorCode == 0x0A:
        return "Gateway path unavailable.";
    elif errorCode == 0x0B:
        return "Gateway target device failed to respond.";
    else:
        return "Unknown error code received.";

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

# Make sure response is even byte length.
if len(response) % 2 == 0:
    print("Error: Response length is uneven. Missing nibble in byte.")
    sys.exit()

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
isACK = FUNC < 0x80
isNAK = FUNC > 0x80

# Parse positive response.
if isACK:
    bytes = DataTypeByteCount(dataType)
    
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
elif isNAK:

    errorCode = response[8]                         # Gets the error code.
    errorMessage = LookupErrorMessage(errorCode)    # Gets the error message.
    print("[NAK]: %s"%(errorMessage))
    
# Unknown response.
else:
    print("Error: Unknown response.")
    sys.exit()
