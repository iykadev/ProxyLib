import socket
from queue import Queue

import packet
import pthread
from log import log


class Handler:

    def __init__(self, self_name=None, peer_name=None, conn=None, self_ip=None, self_port=None, peer_ip=None, peer_port=None, call_back=None, call_back_args=None, log_coms=False):
        self.isConnected = True;
        self.self_name = self_name
        self.peer_name = peer_name
        self.conn = conn
        self.self_ip = self_ip
        self.self_port = self_port
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.call_back = call_back
        self.call_back_args = call_back_args
        self.outgoing_packet_queue = Queue()
        self.log_coms = log_coms

    # sends packet to connection
    def _send_packet(self, packet):
        self.conn.sendall(packet.export())

    # receives a packet from client and adds it to a queue
    def _receive_packet(self, buffer_length):
        return packet.Packet(self.conn.recv(buffer_length))

    def _receive_data(self, buffer_length):
        return self.conn.recv(buffer_length)

    def send_all(self):
        while not self.outgoing_packet_queue.empty():
            self._send_packet(self.outgoing_packet_queue.get())

    def schedule_outgoing_packet(self, packet):
        self.outgoing_packet_queue.put(packet)

    # wrapper for packet sending
    def send_packet(self, packet):
        self.schedule_outgoing_packet(packet)
        if self.log_coms:
            log("<%s>" % self.self_name, packet, '\n')

    # wrapper for packet receiving
    def receive_packet(self, buffer_length):
        packet = self._receive_packet(buffer_length)
        if self.log_coms:
            log("<%s>" % self.peer_name, packet, '\n')
        return packet

    def receive_data(self, buffer_length):
        return self._receive_data(buffer_length)

    def handle_receiving_data(self):
        term_len = packet.STREAM_TERMINATING_BYTE_LEN
        data = bytes()

        while data[-term_len:] != packet.STREAM_TERMINATING_BYTE:
            data += self.receive_data(1)

        data = data[:-term_len]
        data = packet.Packet(data)

        if self.log_coms:
            log("<%s>" % self.peer_name, data, '\n')

        return data

    def handle_connection(self):
        thread = pthread.PThread(self.call_back, (self, *self.call_back_args), is_daemon=False)
        thread.start()
        return thread

    def print_connection_info(self):
        log('connected to:', self.peer_ip + ":" + str(self.peer_port))

    def print_disconnection_info(self):
        log("Connection lost with host:", self.peer_ip + ":" + str(self.peer_port))

    def disconnect(self):
        self.conn.shutdown(socket.SHUT_WR)
