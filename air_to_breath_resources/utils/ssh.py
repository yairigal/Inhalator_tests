import scp
from paramiko import AutoAddPolicy
from paramiko import SSHClient


class SSH:
    def __init__(self, host, user, password):
        self._client = SSHClient()
        self._client.set_missing_host_key_policy(AutoAddPolicy())
        #        self._client.load_system_host_keys()
        self._client.connect(hostname=host,
                             password=password,
                             username=user)

        self._scp = scp.SCPClient(self._client.get_transport())

    def execute(self, cmd, wait=True):
        _, stdout, stderr = self._client.exec_command(cmd)
        if not wait:
            return stdout, stderr

        return stdout.read(), stderr.read()

    def copy(self, local, remote):
        self._scp.put(local, remote_path=remote, recursive=True)
