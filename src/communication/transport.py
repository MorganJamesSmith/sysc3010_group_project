#
#   Transport layer built on top of a ThingSpeak channel.
#   Samuel Dewan - 2020
#

import thingspeak
import base64
from threading import Thread, Event, Timer
from enum import Flag, auto
from multiprocessing import Queue
from queue import Empty

#
#   Transport Layer Protocol
#
#       The transport layer is responsible for delivery of messages between hosts accross a
#       ThingSpeak channel. Every message sent is encoded into a single entry on the ThingSpeak
#       channel with up to the following two fields:
#           Field 1: Header
#               The header contains information related to the transport layer.
#           Field 2: Payload (optional)
#               The payload field contains application layer data.
#       
#       The header contains several fields, each of which is encoded as a string. The fields are
#       seperated by a tab character, meaning that none of the field values may contain a tab. The
#       header contains the following fields (in this order):
#           Source Address
#               A string the uniquely identifies the device tfrom which the message originates.
#           Destination Address
#               A String the uniquely identifies the device for which the message is intended.
#           Flags
#               A '|' seprated list of flags. Each flag is represented by a string.
#       
#       The flags field may consist of any combination of the following flags:
#           "conn_req"
#               Indicates that the message is a connection request. If set, any other flags and the
#               payload are ignored. The connection process is described in more detail below.
#
#       In order to establish a connection, a client will send message to the server to which it
#       wishes to connect that has the conn_req flag set. If the server receives the message and is
#       accepting connections it will respond with a messages that has the conn_req flag set.
#

class TransportLayerFlags(Flag):
    NONE = 0
    CONN_REQ = auto()

    def __str__(self):
        strings = []
        if TransportLayerFlags.CONN_REQ in self:
            strings.append("conn_req")
        return "|".join(strings)

    @classmethod
    def from_string(cls, string):
        out = cls.NONE
        for flag in string.split('|'):
            if flag == "conn_req":
                out |= cls.CONN_REQ
        return out

class TransportLayerHeader:
    def __init__(self, source_addr, dest_addr, flags):
        self.source_addr = source_addr
        self.dest_addr = dest_addr
        self.flags = flags

    def __str__(self):
        return f"{self.source_addr}\t{self.dest_addr}\t{self.flags}"

    @classmethod
    def from_string(cls, string):
        fields = string.split('\t')
        return cls(fields[0], fields[1], TransportLayerFlags.from_string(fields[2]))

class ThingSpeakPoller(Thread):
    def __init__(self, channel):
        Thread.__init__(self)

        self.daemon = True

        self.channel = channel
        self.last_entry = self.channel.get_last_entry_id()

        self.clients = dict()
        self.should_stop = Event()
        self.has_client = Event()

    def run(self):
        while not self.should_stop.is_set():
            # Don't do anything until there is at least one registered client
            self.has_client.wait()

            # Poll for new entries on the ThingSpeak channel
            current_entry_id = 0
            newest_entry_list = self.channel.read(count = 1)
            if not newest_entry_list:
                entry = None
            else:
                entry = newest_entry_list[0]
            if entry:
                current_entry_id = entry['entry_id']
            # If there have been new entries since we last checked, get them all
            num_new_entries = current_entry_id - self.last_entry
            entries = []
            if num_new_entries == 1:
                # There is only one new entry, we already fetched it
                entries = [entry]
            else:
                # There is more than one new entry, we need to fetch them all
                entries = self.channel.read(count = num_new_entries)
            # Update the last entry number we have seen
            self.last_entry = current_entry_id

            # Iterate over entries from oldest to newest
            for e in reversed(entries):
                # Call all of the registered callbacks for each entry
                for cb in self.clients.keys():
                    cb(e)

            if self.has_client.is_set():
                # If we have at least one client, then wait for the polling period of the client
                # that has requested the most frequent polling or until we need to stop
                self.should_stop.wait(timeout = min(self.clients.values()))

    def stop(self):
        self.should_stop.set()
        self.join()

    def register(self, callback, poll_period = 1):
        self.clients[callback] = poll_period
        self.has_client.set()

    def unregister(self, callback):
        self.clients.pop(callback)
        if not self.clients:
            self.has_client.reset()

class ConnectionException(Exception):
    pass

class Connection:
    channel_pollers = dict()

    def __init__(self, channel, address, peer_address, preestablished = False, poll_period = 1,
                server = None):
        self.channel = channel
        self.server = server
        # Addresses
        self.address = address
        self.peer_address = peer_address

        self.poll_period = poll_period
        
        # List of messages that we have tried to send and are waiting for confirmation on
        self.sent_messages = list()
        # Queue of received messages
        self.in_queue = Queue()
        
        self.closed = False

        # Set up poller
        if not channel in Connection.channel_pollers:
            # Create a new poller for this channel
            Connection.channel_pollers[self.channel] = ThingSpeakPoller(channel)
            Connection.channel_pollers[self.channel].start()
        # Register with poller
        Connection.channel_pollers[self.channel].register(self._handle_entry, poll_period)

        # Establish connection if it is not preestablished
        self.established = Event()
        if preestablished:
            self.established.set()
        self._send_conn_req()
        

    def close(self):
        Connection.channel_pollers[self.channel].unregister(self._handle_entry)
        if not Connection.channel_pollers[self.channel].clients:
            # Poller has no more clients
            Connection.channel.pollers.pop(self.channel).stop()
        self.closed = True

        if self.server is not None:
            self.server.unregister_connection(self)

    @staticmethod
    def _entry_matches_sent_message(entry, m):
        return (((m[0] is None and entry['field2'] is None) or
                 ((m[0] is not None and entry['field2'] is not None) and
                  (m[0] == entry['field2'].encode('utf-8')))) and
                (m[1] == entry['field1']))

    def _handle_entry(self, entry):
        header = TransportLayerHeader.from_string(entry['field1'])
        if (header.dest_addr == self.peer_address) and (header.source_addr == self.address):
            # This is a message that we sent, since we know now that it made it to the ThingSpeak
            # channel, we can safely remove it from our list of outgoing messages
            message_info = next((i for i in self.sent_messages if
                                 Connection._entry_matches_sent_message(entry, i)), None)
            if message_info:
                self.sent_messages.remove(message_info)
                message_info[2].cancel()
            return
        elif (header.dest_addr != self.address) or (header.source_addr != self.peer_address):
            # Message is not for this connection
            return
        # Check if this is the start of a new connection
        if TransportLayerFlags.CONN_REQ in header.flags:
            self.established.set()
            return
        # Add received message to in queue
        self.in_queue.put(base64.b64decode(entry['field2']))
   
    def _retry_message(self, payload, header):
        message_info = next((i for i in self.sent_messages if (i[0] == payload) and
                            (i[1] == header)), None)
        if message_info:
            try:
                self.sent_messages.remove(message_info)
            except ValueError:
                return
            # Our message is still in the list of messages to be resent, we should resend it now
            if payload is not None:
                self.channel.write({"field1" : header, "field2" : payload})
            else:
                self.channel.write({"field1" : header})
            # Launch timer to resend message if it fails again
            t = Timer(self.poll_period * 1.5, self._retry_message, args=[payload, header])
            t.start()
            self.sent_messages.append((payload, header, t))

    def fileno(self):
        return self.in_queue._reader.fileno()
        
    def send(self, msg):
        if self.closed:
            raise ConnectionExcpetion("Cannot send on closed connetion.")
        if not self.established.is_set():
            raise ConnectionException("Connetion is not yet established.")
        
        header = TransportLayerHeader(self.address, self.peer_address, TransportLayerFlags.NONE)
        header_str = str(header)
        payload = base64.b64encode(msg)
        
        self.channel.write({"field1" : header_str, "field2" : payload})

        # Launch timer to resend message if it fails
        t = Timer(self.poll_period * 1.5, self._retry_message, args=[payload, header_str])
        t.start()
        self.sent_messages.append((payload, header_str, t))


    def recv(self, block = True, timeout = None):
        try:
            return self.in_queue.get(block=block, timeout=timeout)
        except Empty:
            return None

    def _send_conn_req(self):
        header = TransportLayerHeader(self.address, self.peer_address, TransportLayerFlags.CONN_REQ)
        header_str = str(header)
        self.channel.write({"field1" : header})

        # Launch timer to resend message if it fails
        t = Timer(self.poll_period * 5, self._retry_message, args=[None, header_str])
        t.start()
        self.sent_messages.append((None, header_str, t))


class Server:
    def __init__(self, channel, address, poll_period = 2):
        self.channel = channel
        self.address = address
        self.connection_queue = Queue()

        self.connections = dict()

        self.poller = ThingSpeakPoller(channel)
        self.poller.start()
        self.poller.register(self._handle_entry, poll_period)

    def _handle_entry(self, entry):
        header = TransportLayerHeader.from_string(entry['field1'])
        if not TransportLayerFlags.CONN_REQ in header.flags:
            # Ignore any message that is not a connection request
            return
        if self.address != header.dest_addr:
            # Ignore any message that is not intended for us
            return
        if header.source_addr in self.connections:
            # Ignore connection requests when we already have an estabished connection
            return
        # Send a response to start the connection
        #rsp_header = TransportLayerHeader(self.address, header.source_addr,
        #                                  TransportLayerFlags.CONN_REQ)
        #self.channel.write({"field1" : str(rsp_header)})
        # Add the address to the queue for it to be accepted
        self.connection_queue.put(header.source_addr)

    def accept(self, block = True, timeout = None):
        try:
            peer_address = self.connection_queue.get(block=block, timeout=timeout)
            if peer_address in self.connections:
                con = self.connections[peer_address]
            else:
                con = Connection(self.channel, self.address, peer_address, preestablished = True)
                self.connections[peer_address] = con
            return con, peer_address
        except Empty:
            return None, None

    def fileno(self):
        return self.connection_queue._reader.fileno()

    def unregister_connection(self, connection):
        try:
            self.connections.pop(connection.peer_address)
        except ValueError:
            pass

    def close(self):
        self.poller.stop()

