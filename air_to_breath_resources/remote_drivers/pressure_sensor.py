import socket

PORT = 5555


class HcePressureSensor:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._socket.bind(('0.0.0.0', PORT))
        self._socket.settimeout(0)

    def read_pressure(self):
        try:
            val = float(self._socket.recv(2 ** 16))
            print(f'pressure={val}')
            return val

        except BlockingIOError:
            return 0
