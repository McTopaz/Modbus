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
    UINT8: 1, 1, 0xDE
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
    registers[0] = CreateRegisterValue(1, struct.pack(">h", -1))                    # INT8
    registers[1] = CreateRegisterValue(1, struct.pack(">H", 0x00DE))                # UINT8
    registers[2] = CreateRegisterValue(1, struct.pack(">h", -1))                    # INT16
    registers[3] = CreateRegisterValue(1, struct.pack(">H", 0xDEAD))                # UINT16
    registers[4] = CreateRegisterValue(2, struct.pack(">i", -1))                    # INT24
    registers[6] = CreateRegisterValue(2, struct.pack(">I", 0x00DEADBE))            # UINT24
    registers[8] = CreateRegisterValue(2, struct.pack(">i", -1))                    # INT32
    registers[10] = CreateRegisterValue(2, struct.pack(">I", 0xDEADBEEF))           # UINT32
    registers[12] = CreateRegisterValue(3, struct.pack(">q", -1))                   # INT48
    registers[15] = CreateRegisterValue(3, struct.pack(">Q", 0x0000DEADBEEFBABE))   # UINT48
    registers[18] = CreateRegisterValue(4, struct.pack("q", -1))                    # INT64
    registers[22] = CreateRegisterValue(4, struct.pack(">Q", 0xDEADBEEFBABECAFE))   # UINT64
    registers[26] = CreateRegisterValue(2, struct.pack("f", 0xDEADBEEF))            # REAL32
    registers[28] = CreateRegisterValue(4, struct.pack("d", 0xDEADBEEFBABECAFE))    # REAL64
    registers[32] = CreateRegisterValue(1, bytearray("A", 'ascii'))                 # STR1
    registers[33] = CreateRegisterValue(1, bytearray("AB", 'ascii'))                # STR2
    registers[34] = CreateRegisterValue(2, bytearray("ABCD", 'ascii'))              # STR4
    registers[36] = CreateRegisterValue(3, bytearray("ABCDEF", 'ascii'))            # STR6
    registers[39] = CreateRegisterValue(4, bytearray("ABCDEFGH", 'ascii'))          # STR8
    registers[43] = CreateRegisterValue(5, bytearray("ABCDEFGHIJ", 'ascii'))        # STR10
    registers[48] = CreateRegisterValue(6, bytearray("ABCDEFGHIJKL", 'ascii'))      # STR12
    return registers

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
        
    def ValidateRequest(self):
        # Overload in sub class.
        pass
        
    def IsRegisterDefined(self):
        start = self.start
        count = self.count
        return start in registers and count in registers[start]
        
class ModbusRtuRequest(ModbusRequest):
    def __init__(self,  data):
        ModbusRequest.__init__(self, data, data[0:6])
        self.crc = struct.unpack('h', data[6:8])[0]
        
    def ValidateRequest(self):
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
    
    def ValidateRequest(self):
        okLength = len(self.request) == (6 + self.count)
        okSlaveAddress = self.slaveAddress == slaveAddress
        okFunction = self.function == 0x03 or self.function == 0x04
        return okLength and okSlaveAddress and okFunction
    
#=== Modbus response ==========================================================

class ModbusResponse():
    def __init__(self,  slaveAddress, function):
        self.slaveAddress = slaveAddress
        self.function = function

class ModbusRtuResponse(ModbusResponse):
    def __init__(self,  slaveAddress, function):
        ModbusResponse.__init__(self, slaveAddress, function)
        
    def CreatePositiveResponse(self, data):
        response = struct.pack("BBB", self.slaveAddress, self.function, len(data))
        response += data 
        crc = self.CalculateCRC(response)
        response += struct.pack("H", crc)
        return response
        
    def CreateNegativeResponse(self, error):
        response = struct.pack("BBB", self.slaveAddress, self.function, error)
        crc = self.CalculateCRC(response)
        response += struct.pack("H", crc)
        return response
        
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
        
class ModbusTcpResponse(ModbusResponse):
    def __init__(self,  slaveAddress, function):
        ModbusResponse.__init__(self, slaveAddress, function)
        
    def CreatePositiveResponse(self, data):
        return b""
        
    def CreateNegativeResponse(self, error):
        return b""
        
#=== Modbus server ============================================================
        
class ModbusServer():
    def __init__(self):
        self.request = 0
        self.response = 0
        
    def ParseRequest(self,  request):
        # Overload in sub class.
        pass
        
    def AcceptableRequest(self):
        self.request.ValidateRequest()
        print("Request is valid: %s"%(self.request.valid))
        defined = self.request.IsRegisterDefined()
        print("Register is defined: %s"%(defined))
        return self.request.valid and defined
      
    def CreateResponse(self):
        if (self.AcceptableRequest):
            print("Start: %s"%self.request.start)
            print("Count: %s"%self.request.count)
            data = registers[self.request.start][self.request.count]
            PrintData(data)
            return self.response.CreatePositiveResponse(data)
        else:
            error = 0
            return self.response.CreateNegativeResponse(error)

class ModbusRtuServer(ModbusServer):
    def __init__(self,):
        ModbusServer.__init__(self)
        
    def ParseRequest(self,  request):
        self.request = ModbusRtuRequest(request)
        self.response = ModbusRtuResponse(self.request.slaveAddress, self.request.function)
        
class ModbusTcpServer(ModbusServer):
    def __init___(self):
        ModbusServer.__init__(self)

    def ParseRequest(self,  request):
        self.request = ModbusTcpRequest(request)
        self.response = ModbusTcpResponse(self.request.slaveAddress, self.request.function)

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
    
