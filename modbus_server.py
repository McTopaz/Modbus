#!/usr/bin/python3

import os
import sys
import struct
import socketserver

if len(sys.argv) < 5:
    print("Usage: %s <ip> <port> <transport protcol: udp = UDP tcp = TCP> <data protocol: tcp = Modbus TCP, rtu = Modbus rtu>"%(os.path.basename(sys.argv[0])))
    sys.exit()

print("")
print(sys.argv)
print("")
    
ip = sys.argv[1]
port = int(sys.argv[2])

if sys.argv[3]  != "udp" and sys.argv[3] != "tcp":
    print("Invalid transport protocol")
    sys.exit()

if sys.argv[4] != "tcp" and sys.argv[4] != "rtu":
    print("Invalid data protocol")
    sys.exit()

#=== Misc =====================================================================

def CreateRegisterValue(count, value):
    dict = {}
    dict[count] = value
    return dict

def DefineRegisters():
    ''''
    INT8: 0, 1, -1
    UINT8: 1, 1, 0xAD
    INT16: 2, 1, -1
    UINT16: 3, 1, 0xDEAD
    INT24: 4, 2, -1
    UINT24: 6, 2, 0xDEADBE
    INT32: 8, 2, -1
    UINT32: 10, 2, 0xDEADBEEF
    INT48: 12, 3, -1
    UINT48: 15, 3, 0xDEADBEEFBABE
    INT64: 18, 4, -1
    UINT64: 22, 4, 0xDEADBEEFBABECAFE
    REAL32: 26, 2, 0xDEADBEEF
    REAL64: 28, 4, 0xDEADBEEFBABECAFE
    STR1: 32, 1, A
    STR2: 33, 1, AB
    STR4: 34, 2, ABCD
    STR6: 36, 3, ABCDEF
    STR8: 39, 4, ABCDEFGH
    STR10: 43, 5, ABCDEFGHIJ
    STR12: 48, 6, ABCDEFGHIJKL
    '''
    
    registers = {}
    registers[0] = CreateRegisterValue(1, -1)
    registers[1] = CreateRegisterValue(1, 0xAD)
    registers[2] = CreateRegisterValue(1, 0xAD)
    registers[3] = CreateRegisterValue(1, 0xAD)
    registers[4] = CreateRegisterValue(2, 0xAD)
    registers[6] = CreateRegisterValue(2, 0xAD)
    registers[8] = CreateRegisterValue(2, 0xAD)
    registers[10] = CreateRegisterValue(2, 0xAD)
    registers[12] = CreateRegisterValue(3, 0xAD)
    registers[15] = CreateRegisterValue(3, 0xAD)
    registers[18] = CreateRegisterValue(4, 0xAD)
    registers[22] = CreateRegisterValue(4, 0xAD)
    registers[26] = CreateRegisterValue(2, 0xAD)
    registers[28] = CreateRegisterValue(4, 0xAD)
    registers[32] = CreateRegisterValue(1, 0xAD)
    registers[33] = CreateRegisterValue(1, 0xAD)
    registers[34] = CreateRegisterValue(2, 0xAD)
    registers[36] = CreateRegisterValue(3, 0xAD)
    registers[39] = CreateRegisterValue(4, 0xAD)
    registers[43] = CreateRegisterValue(5, 0xAD)
    registers[48] = CreateRegisterValue(6, 0xAD)
    return registers
    
    '''
    data = struct.pack('bBhHiIiIqQqQfd',
        -1,
        0xAD,
        -1,
        0xDEAD,
        -1,
        0xDEADBE,
        -1,
        0xDEADBEEF,
        -1,
        0xDEADBEEDBABE,
        -1,
        0xDEADBEEFBABECAFE, 
        0xDEADBEEF,
        0x0EADBEEFBABECAFE)
    
    data += b"0A"           # strig[1]
    data += b"AB"           # string[2]
    data += b"0ABC"         # string[3]
    data += b"ABCD"         # string[4]
    data += b"ABCDEF"       # string[6]
    data += b"ABCDEFGH"     # string[8]
    data += b"ABCDEFGHIJ"   # string[10]
    data += b"ABCDEFGHIJKL" # string[12]
    
    return data
    '''

def PrintData(data):
    tstr = ""
    for j in range(len(data)):
        if j%16 == 0 and j != 0:
            tstr = tstr + '\n'
        tstr = tstr + "%02X "%data[j]
    print(tstr) 

def Execute(request):
    response = b""
    server = 0
    
    if dataProtocol == "tcp":
        server = ModbustcpServer()
    elif dataProtocol == "rtu":
        server = ModbusRtuServer()
    else:
        print("Invalid data protocol")
        sys.exit()
    
    server.ParseRequest(request)
    response = server.CreateResponse()
    return response

#=== Servers ==================================================================
    
class UdpServer(socketserver.BaseRequestHandler):
    def handle(self):
        request = self.request[0]   # Gets the request sent from the Modbus client
        socket = self.request[1]    # Gets the Modbus client's network connection
        response = Execute(request)
        socket.sendto(response, self.client_address)    # Send response to Modbus client

class TcpServer(socketserver.BaseRequestHandler):
    def handle(self):
        request = self.request.recv(1024).strip()
        response = Execute(request)
        self.request.sendall(response)

#=== Modbus request ===========================================================
        
class ModbusRequest():
    def __init__(self,  request,  data):
        self.request = request
        self.slaveAddress = data[0]
        self.function = data[1]
        self.start = struct.unpack('>h',  data[2:4])[0]
        self.count = struct.unpack('>h',  data[4:6])[0]
        self.valid = False
        
    def ValidRequest(self):
        # Overload in sub class.
        pass
        
    def IsRegisterDefined(self):
        start = self.start
        count = self.count
        return start in registers and count in registers[start]

        '''
        end = (self.start + self.count) * 2
        print("end: %s"%(end))
        print("len: %s"%(len(registers)))
        return end <= len(registers) and end != -1
        '''
        
class ModbusRtuRequest(ModbusRequest):
    def __init__(self,  data):
        ModbusRequest.__init__(self, data, data[0:6])
        self.crc = struct.unpack('h', data[6:8])[0]
        
    def ValidRequest(self):
        PrintData(self.request)
        calcedCrc = self.CalculateCRC(self.request[0:6])
        okLength = len(self.request) == 8
        okSlaveAddress = self.slaveAddress == slaveAddress
        okFunction = self.function == 0x03 or self.function == 0x04
        okCrc = calcedCrc == self.crc
        self.valid = okLength and okSlaveAddress and okFunction and okCrc
        
    def CalculateCRC(self,  data):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos 
            for i in range(8):
                if ((crc & 1) != 0):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
        
class ModbusTcpRequest(ModbusRequest):
    def __init__(self,  data):
        ModbusRequest.__init__(self, data, data[6:12])
    
    def ValidRequest(self):
        okLength = len(self.request) == (6 + self.count)
        okSlaveAddress = self.slaveAddress == slaveAddress
        okFunction = self.function == 0x03 or self.function == 0x04
        return okLength and okSlaveAddress and okFunction
    
#=== Modbus response ==========================================================

class ModbusResponse():
    def __init__(self):
        pass

class ModbusRtuResponse(ModbusResponse):
    def __init__(self):
        pass
        
class ModbusTcpResponse(ModbusResponse):
    def __init__(self):
        pass

#=== Modbus server ============================================================
        
class ModbusServer():
    def __init__(self):
        self.request = 0
        self.response  = 0
        
    def ParseRequest(self,  request):
        # Overload in sub class.
        pass
        
    def AcceptableRequest(self):
        self.request.ValidRequest()
        print("Request is valid: %s"%(self.request.valid))
        defined = self.request.IsRegisterDefined()
        print("Register is defined: %s"%(defined)
        return self.request.valid and defined
      
    def CreateResponse(self):
        if (self.AcceptableRequest):
            return self.CreatePositiveResponse()
        else:
            return self.CreateNegativeResponse()
            
    def CreatePositiveResponse(self):
        # Overload in sub class.
        pass
        
    def CreateNegativeResponse(self):
        # Overload in sub class.
        pass

class ModbusRtuServer(ModbusServer):
    def __init__(self,):
        ModbusServer.__init__(self)
        
    def ParseRequest(self,  request):
        self.request = ModbusRtuRequest(request)
        
    def CreatePositiveResponse(self):
        return b""
        
    def CreateNegativeResponse(self):
        return b""
        
class ModbusTcpServer(ModbusServer):
    def __init___(self):
        ModbusServer.__init__(self)

    def ParseRequest(self,  request):
        self.request = ModbusTcpRequest(request)
        
    def CreatePositiveResponse(self):
        return b""
        
    def CreateNegativeResponse(self):
        return b""

#=== Main =====================================================================

transportProtocol = sys.argv[3]
dataProtocol = sys.argv[4]
slaveAddress = 1
registers = DefineRegisters()
        
if __name__ == "__main__":
    server = 0
    
    if transportProtocol == "udp":
        server = socketserver.UDPServer((ip,  port),  UdpServer)
    elif transportProtocol == "tcp":
        server = socketserver.TCPServer((ip,  port),  TcpServer)
    else:
        print("Invalid transport protocol")
        sys.exit()
    
    server.serve_forever()
    
