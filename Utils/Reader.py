from io import BufferedReader, BytesIO, SEEK_CUR
import zlib
from Utils.LogicLong import LogicLong
from Utils.Debugger import Debugger
from Utils.ByteStreamHelper import ByteStreamHelper

class ByteStream(BufferedReader):

    def __init__(self, initial_bytes):
        super().__init__(BytesIO(initial_bytes))
        self.payload = initial_bytes
        self.offset = 0
        self.bitoffset = 0


    def readBoolean(self):
        bitoffset = self.bitoffset
        offset = self.offset + (8 - bitoffset >> 3)
        self.offset = offset
        self.bitoffset = bitoffset + 1 & 7
        return (1 << (bitoffset & 31) & self.payload[offset - 1]) != 0
    
    def read_string(self, max=900000):
        self.bitoffset = 0
        length = (self.payload[self.offset] << 24)
        length += (self.payload[self.offset + 1] << 16)
        length += (self.payload[self.offset + 2] << 8)
        length += (self.payload[self.offset + 3])
        self.offset += 4
        if length <= -1:
            if length != -1:
                Debugger.warning("Negative String length encountered.")
            return b''
        elif length > max:
            Debugger.warning(f"Too long String encountered, length {length}, max {max}")
            return b''
        result = bytes(self.payload[self.offset:self.offset + length]).decode('utf-8')
        self.offset += length
        return result

    
    
    def readDataReference(self):
        return ByteStreamHelper.readDataReference(self)

    def readString(self, max=900000):
        self.bitoffset = 0
        length = (self.payload[self.offset] << 24)
        length += (self.payload[self.offset + 1] << 16)
        length += (self.payload[self.offset + 2] << 8)
        length += (self.payload[self.offset + 3])
        self.offset += 4
        if length <= -1:
            if length != -1:
                Debugger.warning("Negative String length encountered.")
            return b''
        elif length > max:
            Debugger.warning(f"Too long String encountered, length {length}, max {max}")
            return b''
        result = bytes(self.payload[self.offset:self.offset + length]).decode('utf-8')
        self.offset += length
        return result
    
    def readStringReference(self, max):
        self.bitoffset = 0
        length = (self.payload[self.offset] << 24)
        length += (self.payload[self.offset + 1] << 16)
        length += (self.payload[self.offset + 2] << 8)
        length += (self.payload[self.offset + 3])
        self.offset += 4
        if length <= -1:
            if length != -1:
                Debugger.warning("Negative String length encountered.")
            return b''
        elif length > max:
            Debugger.warning(f"Too long String encountered, length {length}, max {max}")
            return b''
        result = self.payload[self.offset].decode('utf-8')
        self.offset += length
        return result
    
    def readVLong(self):
        result = []
        result.append(self.readVInt())
        result.append(self.readVInt())
        return result
    
    def read_vint(self):
        offset = self.offset
        self.bitoffset = 0
        v4 = offset + 1
        self.offset = offset + 1
        result = self.payload[offset] & 0x3F
        if (self.payload[offset] & 0x40) != 0:
            if (self.payload[offset] & 0x80) != 0:
                self.offset = offset + 2
                v7 = self.payload[v4]
                v8 = result & 0xFFFFE03F | ((v7 & 0x7F) << 6)
                if (v7 & 0x80) != 0:
                    self.offset = offset + 3
                    v9 = v8 & 0xFFF01FFF | ((self.payload[offset + 2] & 0x7F) << 13)
                    if (self.payload[offset + 2] & 0x80) != 0:
                        self.offset = offset + 4
                        v10 = v9 & 0xF80FFFFF | ((self.payload[offset + 3] & 0x7F) << 20)
                        if (self.payload[offset + 3] & 0x80) != 0:
                            self.offset = offset + 5
                            return v10 & 0x7FFFFFF | (self.payload[offset + 4] << 27) | 0x80000000
                        else:
                            return v10 | 0xF8000000
                    else:
                        return v9 | 0xFFF00000
                else:
                    return v8 | 0xFFFFE000
            else:
                return self.payload[offset] | 0xFFFFFFC0
        elif (self.payload[offset] & 0x80) != 0:
            self.offset = offset + 2
            v6 = self.payload[v4]
            result = result & 0xFFFFE03F | ((v6 & 0x7F) << 6)
            if (v6 & 0x80) != 0:
                self.offset = offset + 3
                result = result & 0xFFF01FFF | ((self.payload[offset + 2] & 0x7F) << 13)
                if (self.payload[offset + 2] & 0x80) != 0:
                    self.offset = offset + 4
                    result = result & 0xF80FFFFF | ((self.payload[offset + 3] & 0x7F) << 20)
                    if (self.payload[offset + 3] & 0x80) != 0:
                        self.offset = offset + 5
                        return result & 0x7FFFFFF | (self.payload[offset + 4] << 27)
        return result
    
    def read_Vint(self):
        offset = self.offset
        self.bitoffset = 0
        v4 = offset + 1
        self.offset = offset + 1
        result = self.payload[offset] & 0x3F
        if (self.payload[offset] & 0x40) != 0:
            if (self.payload[offset] & 0x80) != 0:
                self.offset = offset + 2
                v7 = self.payload[v4]
                v8 = result & 0xFFFFE03F | ((v7 & 0x7F) << 6)
                if (v7 & 0x80) != 0:
                    self.offset = offset + 3
                    v9 = v8 & 0xFFF01FFF | ((self.payload[offset + 2] & 0x7F) << 13)
                    if (self.payload[offset + 2] & 0x80) != 0:
                        self.offset = offset + 4
                        v10 = v9 & 0xF80FFFFF | ((self.payload[offset + 3] & 0x7F) << 20)
                        if (self.payload[offset + 3] & 0x80) != 0:
                            self.offset = offset + 5
                            return v10 & 0x7FFFFFF | (self.payload[offset + 4] << 27) | 0x80000000
                        else:
                            return v10 | 0xF8000000
                    else:
                        return v9 | 0xFFF00000
                else:
                    return v8 | 0xFFFFE000
            else:
                return self.payload[offset] | 0xFFFFFFC0
        elif (self.payload[offset] & 0x80) != 0:
            self.offset = offset + 2
            v6 = self.payload[v4]
            result = result & 0xFFFFE03F | ((v6 & 0x7F) << 6)
            if (v6 & 0x80) != 0:
                self.offset = offset + 3
                result = result & 0xFFF01FFF | ((self.payload[offset + 2] & 0x7F) << 13)
                if (self.payload[offset + 2] & 0x80) != 0:
                    self.offset = offset + 4
                    result = result & 0xF80FFFFF | ((self.payload[offset + 3] & 0x7F) << 20)
                    if (self.payload[offset + 3] & 0x80) != 0:
                        self.offset = offset + 5
                        return result & 0x7FFFFFF | (self.payload[offset + 4] << 27)
        return result
    
    def readVInt(self):
        offset = self.offset
        self.bitoffset = 0
        v4 = offset + 1
        self.offset = offset + 1
        result = self.payload[offset] & 0x3F
        if (self.payload[offset] & 0x40) != 0:
            if (self.payload[offset] & 0x80) != 0:
                self.offset = offset + 2
                v7 = self.payload[v4]
                v8 = result & 0xFFFFE03F | ((v7 & 0x7F) << 6)
                if (v7 & 0x80) != 0:
                    self.offset = offset + 3
                    v9 = v8 & 0xFFF01FFF | ((self.payload[offset + 2] & 0x7F) << 13)
                    if (self.payload[offset + 2] & 0x80) != 0:
                        self.offset = offset + 4
                        v10 = v9 & 0xF80FFFFF | ((self.payload[offset + 3] & 0x7F) << 20)
                        if (self.payload[offset + 3] & 0x80) != 0:
                            self.offset = offset + 5
                            return v10 & 0x7FFFFFF | (self.payload[offset + 4] << 27) | 0x80000000
                        else:
                            return v10 | 0xF8000000
                    else:
                        return v9 | 0xFFF00000
                else:
                    return v8 | 0xFFFFE000
            else:
                return self.payload[offset] | 0xFFFFFFC0
        elif (self.payload[offset] & 0x80) != 0:
            self.offset = offset + 2
            v6 = self.payload[v4]
            result = result & 0xFFFFE03F | ((v6 & 0x7F) << 6)
            if (v6 & 0x80) != 0:
                self.offset = offset + 3
                result = result & 0xFFF01FFF | ((self.payload[offset + 2] & 0x7F) << 13)
                if (self.payload[offset + 2] & 0x80) != 0:
                    self.offset = offset + 4
                    result = result & 0xF80FFFFF | ((self.payload[offset + 3] & 0x7F) << 20)
                    if (self.payload[offset + 3] & 0x80) != 0:
                        self.offset = offset + 5
                        return result & 0x7FFFFFF | (self.payload[offset + 4] << 27)
        return result

        
    def readByte(self):
        self.bitoffset = 0
        result = self.payload[self.offset]
        self.offset += 1
        return result


    def ReadBool(self):
        bitoffset = self.bitoffset
        offset = self.offset + (8 - bitoffset >> 3)
        self.offset = offset
        self.bitoffset = bitoffset + 1 & 7
        return (1 << (bitoffset & 31) & self.payload[offset - 1]) != 0

    def readLong(self, logicLong=None):
        if not logicLong:
            logicLong = LogicLong(0, 0)
        logicLong.decode(self)
        return [logicLong.high, logicLong.low]

    def readInt16(self):
        self.bitoffset = 0
        result = (self.payload[self.offset] << 8)
        result += (self.payload[self.offset + 1])
        self.offset += 2
        return result

    def readInt24(self):
        self.bitoffset = 0
        result = (self.payload[self.offset] << 16)
        result += (self.payload[self.offset + 1] << 8)
        result += (self.payload[self.offset + 2])
        self.offset += 3
        return result

    def readInt(self):
        self.bitoffset = 0
        result = (self.payload[self.offset] << 24)
        result += (self.payload[self.offset + 1] << 16)
        result += (self.payload[self.offset + 2] << 8)
        result += (self.payload[self.offset + 3])
        self.offset += 4
        return result

    def read_int(self):
        self.bitoffset = 0
        result = (self.payload[self.offset] << 24)
        result += (self.payload[self.offset + 1] << 16)
        result += (self.payload[self.offset + 2] << 8)
        result += (self.payload[self.offset + 3])
        self.offset += 4
        return result

    def readInt8(self):
        self.bitoffset = 0
        result = (self.messagePayload[self.offset])
        self.offset += 1
        return result

    def readShort(self):
        self.bitoffset = 0
        result = (self.payload[self.offset] << 8)
        result += (self.payload[self.offset + 1])
        self.offset += 2
        return result

    def ReadVint(self):
        offset = self.offset
        self.bitoffset = 0
        v4 = offset + 1
        self.offset = offset + 1
        result = self.payload[offset] & 0x3F
        if (self.payload[offset] & 0x40) != 0:
            if (self.payload[offset] & 0x80) != 0:
                self.offset = offset + 2
                v7 = self.payload[v4]
                v8 = result & 0xFFFFE03F | ((v7 & 0x7F) << 6)
                if (v7 & 0x80) != 0:
                    self.offset = offset + 3
                    v9 = v8 & 0xFFF01FFF | ((self.payload[offset + 2] & 0x7F) << 13)
                    if (self.payload[offset + 2] & 0x80) != 0:
                        self.offset = offset + 4
                        v10 = v9 & 0xF80FFFFF | ((self.payload[offset + 3] & 0x7F) << 20)
                        if (self.payload[offset + 3] & 0x80) != 0:
                            self.offset = offset + 5
                            return v10 & 0x7FFFFFF | (self.payload[offset + 4] << 27) | 0x80000000
                        else:
                            return v10 | 0xF8000000
                    else:
                        return v9 | 0xFFF00000
                else:
                    return v8 | 0xFFFFE000
            else:
                return self.payload[offset] | 0xFFFFFFC0
        elif (self.payload[offset] & 0x80) != 0:
            self.offset = offset + 2
            v6 = self.payload[v4]
            result = result & 0xFFFFE03F | ((v6 & 0x7F) << 6)
            if (v6 & 0x80) != 0:
                self.offset = offset + 3
                result = result & 0xFFF01FFF | ((self.payload[offset + 2] & 0x7F) << 13)
                if (self.payload[offset + 2] & 0x80) != 0:
                    self.offset = offset + 4
                    result = result & 0xF80FFFFF | ((self.payload[offset + 3] & 0x7F) << 20)
                    if (self.payload[offset + 3] & 0x80) != 0:
                        self.offset = offset + 5
                        return result & 0x7FFFFFF | (self.payload[offset + 4] << 27)
        return result

    def readLongLong(self):
        self.bitoffset = 0
        high = (self.payload[self.offset] << 24)
        high += (self.payload[self.offset + 1] << 16)
        high += (self.payload[self.offset + 2] << 8)
        high += (self.payload[self.offset + 3])
        self.offset += 4
        low = (self.payload[self.offset] << 24)
        low += (self.payload[self.offset + 1] << 16)
        low += (self.payload[self.offset + 2] << 8)
        low += (self.payload[self.offset + 3])
        self.offset += 4
        return LogicLong.toLong(high, low)


    def ReadLong(self, logicLong=None):
        if not logicLong:
            logicLong = LogicLong(0, 0)
        logicLong.decode(self)
        return [logicLong.high, logicLong.low]
    
    def ReadString(self, max=900000):
        self.bitoffset = 0
        length = (self.payload[self.offset] << 24)
        length += (self.payload[self.offset + 1] << 16)
        length += (self.payload[self.offset + 2] << 8)
        length += (self.payload[self.offset + 3])
        self.offset += 4
        if length <= -1:
            if length != -1:
                Debugger.warning("Negative String length encountered.")
            return b''
        elif length > max:
            Debugger.warning(f"Too long String encountered, length {length}, max {max}")
            return b''
        result = bytes(self.payload[self.offset:self.offset + length]).decode('utf-8')
        self.offset += length
        return result

    def readBytesLength(self):
        self.bitoffset = 0
        result = (self.payload[self.offset] << 24)
        result += (self.payload[self.offset + 1] << 16)
        result += (self.payload[self.offset + 2] << 8)
        result += (self.payload[self.offset + 3])
        self.offset += 4
        return result

    def readLongLong(self):
        self.bitoffset = 0
        high = (self.payload[self.offset] << 24)
        high += (self.payload[self.offset + 1] << 16)
        high += (self.payload[self.offset + 2] << 8)
        high += (self.payload[self.offset + 3])
        self.offset += 4
        low = (self.payload[self.offset] << 24)
        low += (self.payload[self.offset + 1] << 16)
        low += (self.payload[self.offset + 2] << 8)
        low += (self.payload[self.offset + 3])
        self.offset += 4
        return LogicLong.toLong(high, low)
    
    def readBytes(self, length, max=1000):
        self.bitoffset = 0
        if (length & 0x80000000) != 0:
            if length != -1:
                Debugger.warning("Negative readBytes length encountered.")
        elif length <= max:
            result = self.payload[self.offset:self.offset + length]
            self.offset += length
            return bytes(result)
        else:
            Debugger.warning("readBytes too long array, max", max)
        return b''

    def readIntLittleEndian(self):
        self.bitoffset = 0
        result = (self.payload[self.offset])
        result += (self.payload[self.offset + 1] << 8)
        result += (self.payload[self.offset + 2] << 16)
        result += (self.payload[self.offset + 3] << 24)
        self.offset += 4
        return result

    def decodeLogicLong(self, logicLong=None):
        return ByteStreamHelper.decodeLogicLong(self, logicLong)
    
    def decodeIntList(self):
        return ByteStreamHelper.decodeIntList(self)
    
    def decodeLogicLongList(self):
        return ByteStreamHelper.decodeLogicLongList(self)
    
    def readCompressedString(self):
        data_length = self.readInt()
        if data_length != 4294967295:
            self.readIntLittleEndian()
            return zlib.decompress(self.readBytes(data_length - 4))
        
    def readShort(self):
        self.bitoffset = 0
        result = (self.payload[self.offset] << 8)
        result += (self.payload[self.offset + 1])
        self.offset += 2
        return result
    
    def ReadHexa(self, length):
        return self.read(length).hex()
