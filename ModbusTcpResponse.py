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

Response format:
[TID TID] [PID PID] [LEN LEN] ADR FUNC COUNT [DATA DATA]
'''

import sys

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
    
# Check data type.
if ValidDataType(dataType) == False:
    print("Error: Invalid data type.")
    sys.exit()

sys.exit()
    
# Check response.
if len(response) < 11:
    print("Invalid response length.")
    sys.exit()
    
   # Get response from arguments.
response = []

# Iterate over every other characters.
for start in range(0, len(sys.argv[3]), 2):

    # Try to convert hex string to int.
    try:
        temp = int(sys.argv[1][start:start + 2], 16)
        response.append(temp)
    except:
        print("Error: '%s' contains a non hexadecimal number."%(sys.argv[1]))
        sys.exit()
        
