import socket

PORT = 6666

# THIS CODE SHOULD BE EXACTLY LIKE THE REMOTE DRIVER API

class MockAirFlowSensor:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._socket.bind(('0.0.0.0', PORT))
        self._socket.settimeout(0)

        self.value = 0


    def soft_reset(self):
        pass

    def read_flow_slm(self, retries=2):
        try:
            val = float(self._socket.recv(2 ** 16))
            self.value = val

        except BlockingIOError:
            pass

        finally:
            return self.value
