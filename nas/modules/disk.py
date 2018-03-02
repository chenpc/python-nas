from nas.utils.command import exec_command
from larva.core import LarvaObject
import json
from collections import OrderedDict


class Disk(LarvaObject):

    def __init__(self):
        pass

    def _start(self):
        pass

    def list(self, status="ALL"):
        """ List all disks
        Args:
            status(str):  Get all/free/used disks :enum=["ALL", "FREE", "ONLINE", "UNINITIATED", "INITIATING"]
        Returns:
            disk_list(dict): a list of disks
        Raises:
            NameError(str): Status is not exist
        """

        output = json.loads(exec_command('lsblk -J').stdout)['blockdevices']
        return output
