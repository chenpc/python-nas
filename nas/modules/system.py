from nas.utils.command import exec_command
from larva.core import LarvaObject
from collections import OrderedDict
import tarfile
import glob

class System(LarvaObject):

    def __init__(self):
        pass

    def _start(self):
        pass

    def restore(self):
        """ Restore config files
        """
        tar = tarfile.open("/media/realroot/config.tar", "r")
        tar.extractall(path='/')
        tar.close()

    def backup(self):
        """ Backup System Config
        """
        config_files = ['/etc/passwd', '/etc/group', '/etc/shadow',
                        '/var/lib/samba/private/passdb.tdb',
                        '/var/db/larva.db']
        networkmgmt = glob.glob('/var/lib/NetworkManager/*.conf')

        tar = tarfile.open("/media/realroot/config.tar", "w")
        for name in config_files+networkmgmt:
            tar.add(name)
        tar.close()

    def reboot(self):
        """ Reboot
        """
        exec_command("reboot")

    def poweroff(self):
        """ Power OFF
        """
        exec_command("poweroff")
