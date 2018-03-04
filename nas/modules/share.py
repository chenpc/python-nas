from nas.utils.command import exec_command
from larva.core import LarvaObject
import json
from collections import OrderedDict


class Share(LarvaObject):

    def __init__(self):
        exec_command('mkdir -p /var/lib/samba/usershares')
        exec_command('chmod 1700 /var/lib/samba/usershares')

    def _start(self):
        pass

    def create(self, pool_name, share_name):
        """ Create share folder
        Args:
            pool_name(str): Pool name :func=["pool", "list"]
            share_name(str): Share name
            NameError(str): Status is not exist
        """
        if pool_name not in self.modules.pool.list():  # check pool not exist
            raise NameError("pool not exists", pool_name)

        exec_command('zfs create %s/%s' % (pool_name, share_name))

    def destroy(self, pool_name, share_name):
        """ Create share folder
        Args:
            pool_name(str): Pool name :func=["pool", "list"]
            share_name(str): Share name
            NameError(str): Status is not exist
        """
        if pool_name not in self.modules.pool.list():  # check pool not exist
            raise NameError("pool not exists", pool_name)

        exec_command('zfs destroy %s/%s' % (pool_name, share_name))

    def list(self, pool_name):
        """ List all share folders
        Returns:
            share_list(list): A list of share folders
        """
        output = exec_command('zfs list %s' % pool_name).stdout