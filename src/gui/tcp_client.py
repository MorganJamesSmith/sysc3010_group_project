import socket
import gevent
from gevent.event import Event
from gevent.select import select
from queue import Queue

from waitable_event import WaitableEvent

class TCPClientWorker(gevent.Greenlet):
    def __init__(self, address, port, callback):
        gevent.Greenlet.__init__(self)
        self.daemon = True

        self.address = address
        self.port = port
        self.callback = callback

        self.out_queue = Queue()

        self.connected = Event()
        self.should_stop = WaitableEvent()
        self.new_output = WaitableEvent()

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.address, self.port))
        self.sock.setblocking(0)

        self.connected.set()

        while not self.should_stop.is_set():
            r, w, e = select([self.sock, self.should_stop, self.new_output],
                             [self.sock] if not self.out_queue.empty() else [], [self.sock])

            if self.should_stop in r:
                self.sock.close()
                return

            if self.new_output in r:
                self.new_output.clear()

            if self.sock in r:
                data = self.sock.recv(1024)
                if data:
                    self.callback(data)
                else:
                    self.sock.close()
                    self.should_stop.set()
                    return

            if self.sock in w:
                try:
                    msg = self.out_queue.get_nowait()
                except queue.Empty:
                    pass
                else:
                    self.sock.send(msg)

            if self.sock in e:
                self.sock.close()
                self.should_stop.set()
                return

    def send(self, data):
        self.out_queue.put(data)
        self.new_output.set()

    def stop(self):
        self.should_stop.set()

