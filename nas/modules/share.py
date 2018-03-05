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
        Raises:
            NameError(str): Status is not exist
        """
        if pool_name not in self.modules.pool.list():  # check pool not exist
            raise NameError("pool not exists", pool_name)

        exec_command('zfs create %s/%s' % (pool_name, share_name))
        self.enable(pool_name+'/'+share_name)

    def destroy(self, share_name):
        """ Create share folder
        Args:
            share_name(str): Share name:func=["share", "list"]
        Raises:
            NameError(str): Status is not exist
        """

        exec_command('zfs destroy %s' % share_name)

    def list(self, pool_name=None):
        """ List all share folders
        Args:
            pool_name(str): Pool name :func=["pool", "list"]
        Returns:
            share_list(list): A list of share folders
        """
        res = OrderedDict()
        output = exec_command('zfs list -t filesystem -o name,avail,used,mountpoint').stdout
        for line in output.splitlines()[1:]:
            dataset_name , avail, used, mountpoint = line.split()
            if '/' not in dataset_name:
                continue
            if pool_name is None or pool_name+'/' == dataset_name[0:len(pool_name+'/')]:
                name = dataset_name
                res[name] = OrderedDict()
                res[name]['used'] = used
                res[name]['availible'] = avail
                res[name]['pool'] = dataset_name.split('/')[0]
                res[name]['mountpoint'] = mountpoint

        return res

    def enable(self, share_name):
        """ Enable file share
        Args:
            share_name(str): Share name:func=["share", "list"]
        Raises:
            NameError(str): Status is not exist
        """

        exec_command('zfs set sharesmb=on %s' % share_name)
        exec_command('zfs set acltype=posixacl %s' % share_name)

    def disable(self, pool_name, share_name):
        """ Disable file share
        Args:
            pool_name(str): Pool name :func=["pool", "list"]
            share_name(str): Share name
        Raises:
            NameError(str): Status is not exist
        """
        if pool_name not in self.modules.pool.list():  # check pool not exist
            raise NameError("pool not exists", pool_name)

        try:
            exec_command('zfs set sharesmb=off %s/%s' % (pool_name, share_name))
        except:
            pass
