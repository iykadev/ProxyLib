PACKET_ID_FUNC_INIT = 0
PACKET_ID_FUNC_CALL = 1
PACKET_ID_FUNC_CALL_RETURN = 2
PACKET_ID_FUNC_CALL_ERROR = 3

STREAM_TERMINATING_BYTE = b'\end'
STREAM_TERMINATING_BYTE_STRING = '\end'

STREAM_TERMINATING_BYTE_LEN = len(STREAM_TERMINATING_BYTE)


class Packet:
    __slots__ = ['data', 'packet_id']

    # If packet data is bytes then assumed that packet_id is embedded else assumed otherwise
    def __init__(self, data, packet_id=-1):
        if isinstance(data, bytes):
            self.data = self._decode(data)
            self.de_prefix()
        else:
            self.data = data
            self.packet_id = packet_id

    def export(self):
        return str.encode(bin(self.packet_id)[2:].zfill(16) + self.data) + STREAM_TERMINATING_BYTE

    def get_data(self):
        return self.data

    def de_prefix(self):
        self.packet_id = int(self.data[:16], 2)
        self.data = self.data[16:]

    def _encode(self, b=None):
        return str.encode(self.data) if b is None else str.encode(b)

    def _decode(self, b=None):
        return self.data.decode('utf8') if b is None else b.decode('utf8')

    def __str__(self):
        return '{\n\tPacket-ID: ' + str(self.packet_id) + '\n\tData: ' + str(self.data) + "\n}"
