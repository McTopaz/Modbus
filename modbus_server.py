#!/usr/bin/python3

import os
import sys
import struct
import socketserver

if len(sys.argv) < 5:
    print("Usage: %s <ip> <port> <transport protcol: udp = UDP tcp = TCP> <data protocol: tcp = Modbus TCP, rtu = Modbus rtu>"%(os.path.basename(sys.argv[0])))
    sys.exit()

ip = sys.argv[1]
port = int(sys.argv[2])

if sys.argv[3]  != "udp" and sys.argv[3] != "tcp":
    print("Invalid transport protocol")
    sys.exit()

if sys.argv[4] != "tcp" and sys.argv[4] != "rtu":
    print("Invalid data protocol")
    sys.exit()
    
transportProtocol = sys.argv[1]
dataProtocol = sys.argv[2]

def RegisterIsDefined(request):
    ''''
    INT8: 0, 1, 0xDE
    UINT8: 1, 1, 0xAD
    INT16: 2, 1, 0xDEAD
    UINT16: 3, 1, 0xDEAD
    INT24: 4, 2, 0xDEADBE
    UINT24: 6, 2, 0xDEADBE
    INT32: 8, 2, 0xDEADBEEF
    UINT32: 10, 2, 0xDEADBEEF
    INT48: 12, 3, 0xDEADBEEDBABE
    UINT48: 15, 3, 0xDEADBEEFBABE
    INT64: 18, 4, 0xDEADBEEFBABECAFE
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
    
    data = struct.pack('bBhHiIqQqQfd',
        0xDE,
        0xAD,
        0xDEAD,
        0xDEAD,
        0xDEADBE,
        0xDEADBE,
        0xDEADBEEF,
        0xDEADBEEF,
        0xDEADBEEDBABE,
        0xDEADBEEDBABE,
        0xDEADBEEFBABECAFE,
        0xDEADBEEFBABECAFE, 
        0xDEADBEEF, 
        0xDEADBEEFBABECAFE)
        
    data += b"0A"                     # strig[1]
    data += b"AB"                     # string[2]
    data += b"0ABC"                 # string[3]
    data += b"ABCD"                 # string[4]
    data += b"ABCDEF"             # string[6]
    data += b"ABCDEFGH"         # string[8]
    data += b"ABCDEFGHIJ"     # string[10]
    data += b"ABCDEFGHIJKL" # string[12]
    
    return False

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

class ModbusRequest():
    def __init__(self,  request,  data):
        self.request = request
        self.slaveAddress = data[0]
        self.function = data[1]
        self.start = struct.unpack('h',  data[2:4])[0]
        self.count = struct.unpack('h',  data[4:6])[0]
        
    def ValidRequest(self):
        pass
        
class ModbusRtuRequest(ModbusRequest):
    def __init__(self,  data):
        ModbusRequest.__init__(self, data, data[0:6])
        self.crc = struct.unpack('h', data[6:8])
        
    def ValidRequest(self):
        calcedCrc = self.CalculateCRC(self.request[0:6])
        okLength = len(self.request) == (6 + self.count)
        okCrc = calcedCrc == self.Crc
        return okLength and okCrc
        
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
        okLength = len(self.request) == (10 + self.count)
        return okLength
    

class ModbusResponse():
    def __init__(self):
        pass

class ModbusRtuResponse(Modbusresponse):
    def __init__(self):
        pass
        
class ModbusTcpResponse(ModbusResponse):
    def __init__(self):
        pass

class ModbusServer():
    def __init__(self):
        self.request = 0
        self.response  = 0
        
    def ParseRequest(self,  request):
        pass
        
    def AcceptableRequest(self):
        valid = self.request.ValidRequest()
        defined = RegisterIsDefined(self.request)
        return valid and defined
      
    def CreateResponse(self):
        if (self.AcceptableRequest):
            return self.CreatePositiveResponse()
        else:
            return self.CreateNegativeResponse()
            
    def CreatePositiveResponse(self):
        pass
        
    def CreateNegativeResponse(self):
        pass

class ModbusRtuServer(ModbusServer):
    def __init__(self,):
        ModbusServer.__init__(self)
        
    def ParseRequest(self,  request):
        sef.request = ModbusRtuRequest(request)
        
    def CreatePositiveResponse(self):
        pass
        
    def CreateNegativeResponse(self):
        pass
        
class ModbusTcpServer(ModbusServer):
    def __init___(self):
        ModbusServer.__init__(self)
        
    def CreatePositiveResponse(self):
        pass
        
    def CreateNegativeResponse(self):
        pass

if __name__ == "__main__":
    server = 0
    
    if transportProtocol == "udp":
        server = socketserver.UDPServer((ip,  port),  UdpServer)
    elif transportProtocol == "tcp":
        server = socketserver.TCPServer((ip,  port),  TcpServer)
    else:
        print("Invalid transport protocol")
        sys.eexit()
    
    server.serve_forever()
    
