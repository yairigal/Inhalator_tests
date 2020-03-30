import pickle
import re
import socket
from threading import Thread

import waiting
from cached_property import cached_property


class LogReader:
    PORT = 7878
    SOCKET_TIMEOUT = 2

    def __init__(self, port=PORT):
        self._reading = True
        self.buffer = ''
        self.port = port

    def start_logger(self):
        self._reading = True
        self.thread = Thread(target=self.read_log_from_socket)
        self.thread.start()

    def stop(self):
        self._reading = False
        self.thread.join()
        self.log_socket.close()

    def read_log_from_socket(self):
        self.log_socket.settimeout(self.SOCKET_TIMEOUT)
        while self._reading:
            try:
                log = self.log_socket.recv(2 ** 16)
                log = log[4:]
                log = pickle.loads(log)
                self.buffer += log['msg'] + '\n'

            except socket.timeout:
                pass

    @cached_property
    def log_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.port))
        return sock

    def clear_buffer(self):
        del self.buffer
        self.buffer = ''

    def search(self, regex):
        res = re.findall(regex, self.buffer)
        if len(res) > 0:
            return res[-1]

    def wait_for_log(self, regex, timeout=10, timeout_seconds=1):
        waiting.wait(lambda: self.search(regex) is not None,
                     timeout_seconds=timeout,
                     sleep_seconds=timeout_seconds)
        return self.search(regex)
