'''
Creates a Modbus TCP request to read one single object.

Input:
	* TID: The transmission identifier.
    * Address: The Modbus slave address.
    * Function: The Modbus function, in hex.
	* Register: The register to read from, in hex.
	* Data type: The data type to read, as a character. See data types.
	Example: .\ModbusTcpRequest.py <tid> <address> <function> <register> <data type>
Output:
	A string with the request in hex bytes.
	Example: 0000000000060103000A0002.

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

Request format:
[TID TID] [PID PID] [LEN LEN] ADR FUNC [START START] [COUNT COUNT]

Note:
	* PID parameter is set to [0x00 0x00].
	* LEN is always 6 [0x00 0x06].
'''

import sys
import random

pid = "0000"
length = "0006"

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

# Gets the register count of a data type.
def DataTypeRegisterCount(dataType):
	if dataType == '?':		# BOOL.
		return "0001"
	elif dataType == 'b':	# INT8.
		return "0001"
	elif dataType == 'B':	# UINT8.
		return "0001"
	elif dataType == 'h':	# INT16.
		return "0001"
	elif dataType == 'H':	# UINT16.
		return "0001"
	elif dataType == 'i':	# INT32.
		return "0002"
	elif dataType == 'I':	# UINT32.
		return "0002"
	elif dataType == 'q':	# INT64.
		return "0004"
	elif dataType == 'Q':	# UINT64.
		return "0004"
	elif dataType == 'f':	# REAL32.
		return "0002"
	elif dataType == 'd':	# REAL64.
		return "0004"
	# String data type.
	elif 's' in dataType:
		characters = dataType[1:]	# Get characters after 's'.
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
		elif value == 1:	# s1
			return "0001"
		else:
			count = value / 2 # s2 to s255.
			return "%04X"%(count)
	else:
		print("Error: Unknown data type.")
		sys.exit()

# Check amount of args.
if len(sys.argv) < 6:
    print("Error: Too few arguments.")
    sys.exit()

# Get arguments.
tid = sys.argv[1]       # The TID.
address = sys.argv[2]	# The address (slave address).
function = sys.argv[3]	# The function.	
register = sys.argv[4]	# The register.
dataType = sys.argv[5]	# The data type.

# Check TID.
if tid.isdigit() == False or int(tid) > 0xFFFF:
    print("Error: Invalid TID.")
    sys.exit()

# Check address.
if address.isdigit() == False or int(address) > 0xFF:
	print("Error: Invalid address.")
	sys.exit()

# Check function.
if function.isdigit() == False or int(function) > 0xFF:
	print("Error: Invalid function.")
	sys.exit()
	
# Check register.
if register.isdigit == False or int(register) > 0xFFFF:
	print("Error: Invalid register.")
	sys.exit()

# Check data type.
if ValidDataType(dataType) == False:
    print("Error: Invalid data type.")
    sys.exit()
    
# Parse parameters to hex values.
tid = "%04X"%(int(tid))                 # Get TID as four digit hex value.
adr = "%02X"%(int(address))				# Get the address as two digit hex value.
func = "%02X"%(int(function))			# Get function as two digit hex value.
reg = "%04X"%(int(register))			# Get register as four digit hex value.
count = DataTypeRegisterCount(dataType)	# Get register count based on data type.
	
# Create the request.
request = "%s%s%s%s%s%s%s"%(tid, pid, length, adr, func, reg, count)
print(request)
