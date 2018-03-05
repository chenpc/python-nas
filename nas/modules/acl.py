from nas.utils.command import exec_command
from larva.core import LarvaObject
import json
from collections import OrderedDict


class Acl(LarvaObject):

    def __init__(self):
        pass

    def _start(self):
        pass

    def list(self, pool_name, share_name):
        """ List all disks
        Args:
            status(str):  Get all/free/used disks :enum=["ALL", "FREE", "ONLINE", "UNINITIATED", "INITIATING"]
        Returns:
            disk_list(dict): a list of disks
        Raises:
            NameError(str): Status is not exist
        """

        lsblk_output = json.loads(exec_command('lsblk -JO').stdout)['blockdevices']
        output = OrderedDict()
        for dev in lsblk_output:
            disk = OrderedDict()
            disk['size'] = dev['size']
            disk['type'] = dev['type']
            disk['mountpoint'] = dev['mountpoint']
            disk['label'] = dev['label']
            disk['model'] = dev['model']
            disk['serial'] = dev['serial']

            output[dev['name']] = disk

        return output

    def set_user_acl(self, folder, user, permission):
        """ Set user ACL of folder
        Args:
            folder(str): Folder to set:func=["share", "list"]
            user(str): User name:func=["user", "list"]
            permission(str): Access permission:enum=["RO", "RW", "DA"]
        Exmaples:
            set_user_acl("folder1", "admin", "RO")
            RO: Read only
            RW: Read Write
            DA: Deny access
        Raises:
            TypeError(str): No such persmisison type
        """
        enum = {"RO": "r-", "RW": "rwX", "DA": "---"}
        if permission not in enum:
            raise TypeError("No such permisison type")
        acl = enum[permission]

        folder_info = self.modules.share.list()[folder]
        path = folder_info['mountpoint']
        exec_command('setfacl -R -m u:{}:{} {}'.format(user, acl, path))