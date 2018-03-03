from nas.utils.command import exec_command
from larva.core import LarvaObject
import json
from collections import OrderedDict


class Pool(LarvaObject):

    def __init__(self):
        exec_command('/sbin/modprobe zfs')
        exec_command('zpool import -a')

    def _start(self):
        pass

    def list(self):
        """ List all pools
        Returns:
            pool_list(dict): a list of pool
        """

        zpool_output = exec_command('zpool list -o name,size,alloc,free,health').stdout
        output = OrderedDict()
        for line in zpool_output.splitlines()[1:]:
            name, size, alloc, free, health = line.split()
            pool = OrderedDict()
            pool['size'] = size
            pool['alloc'] = alloc
            pool['free'] = free
            pool['health'] = health

            output[name] = pool

        return output

    def info(self, name):
        """ Get pool info
        Args:
            name(str): Pool name:func=["pool", "list"]
        Returns:
            pool_info(dict): Pool info
        """
        zpool_output = exec_command('zpool status %s' % name).stdout
        prop_output = exec_command('zpool get all %s' % name).stdout

        lines = zpool_output.splitlines()
        state = lines[1].split(':')[1].strip()

        disk_list = list()
        for line in lines[7:-1]:
            if len(line.strip()) != 0:
                disk_list.append(line.strip().split()[0])

        info = OrderedDict()
        props = dict()

        for line in prop_output.splitlines()[1:]:
            name , prop, value, source = line.split()
            props[prop] = value

        info['size'] = props['size']
        info['allocated'] = props['allocated']
        info['capacity'] = props['capacity']
        info['free'] = props['free']
        info['failmode'] = props['failmode']
        info['health'] = props['health']

        info['disk_list'] = disk_list
        return info

    def create(self, name, disk_list, raid_type=""):
        """Create pool
        Args:
            name(str): Pool name
            disk_list(list): A list of disk:func=["disk", "list"]
            raid_type(str): RAID type:enum=["raidz", "raidz2", "raidz3", "mirror"]
        Raises:
            NameError(str): Pool name exist or invalid
            ValueError(str): Disk name is invalid
            TypeError(str): RAID type invalid
        Examples:
            Take a pool name, and then select the disk you want, select the raid type.
            >> pool create name p1 disk_list disk0,disk1 raid_type mirror
        """
        if name in self.list():  # check pool not exist
            raise NameError("pool exists", name)

        if name.isdigit():
            raise NameError("Pool name can not be digit")

        if raid_type != "" and raid_type not in ["raidz", "raidz2", "raidz3", "mirror"]:
            raise TypeError("RAID type: %s is invalid" % raid_type)

        exec_command('zpool create -f %s %s %s' %(name, raid_type, " ".join(disk_list)))

    def destroy(self, name):
        """Create pool
        Args:
            name(str): Pool name
        Raises:
            NameError(str): Pool name exist or invalid
        """
        if name not in self.list():  # check pool not exist
            raise NameError("pool not exists", name)

        exec_command('zpool destroy %s' % name)