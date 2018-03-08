from nas.utils.command import exec_command
from larva.core import LarvaObject
from collections import OrderedDict
import NetworkManager
from enum import IntEnum
import ipaddress
import uuid

class DeviceType(IntEnum):
    ethernet = 1
    bond = 10
    vlan = 11

class DeviceState(IntEnum):
    connected = 100
    connecting = 70
    disconnected = 30


def get_dev_list():
    for dev in NetworkManager.NetworkManager.GetDevices():
        if dev.DeviceType == DeviceType.bond or dev.DeviceType == DeviceType.ethernet:
            yield dev


def get_device(dev_name):
    for dev in get_dev_list():
        if dev.Interface == dev_name:
            return dev
    return None

def get_connection(dev_name):
    return get_device(dev_name).ActiveConnection


class Network(LarvaObject):

    def __init__(self):
        pass

    def _start(self):
        pass

    def list(self):
        """ List all networks
        Returns:
            network_list(dict): a list of networks
        """

        net_list = OrderedDict()
        for dev in get_dev_list():
            netif = OrderedDict()
            if dev.Ip4Config.Addresses:
                netif['Addresses'] = dev.Ip4Config.Addresses[0][0]
                netif['Netmask'] = dev.Ip4Config.Addresses[0][1]
                netif['Gateway'] = dev.Ip4Config.Gateway
            else:
                netif['Addresses'] = ""
                netif['Netmask'] = ""
                netif['Gateway'] = ""
            netif['HwAddress'] = dev.HwAddress
            netif['State'] = DeviceState(dev.State).name
            net_list[dev.Interface] = netif
        return net_list

    def dhcp(self, ifname):
        """ Set network interface to dhcp mode
        Args:
            ifname(str): Interface name :func=["network", "list"]
            vlan_id(int): vlan id
        Raises:
            NameError(str): ifname invalid
        """
        dev = get_device(ifname)
        if dev is None:
            raise NameError('no such interface', ifname)

        if dev.ActiveConnection:
            dev.ActiveConnection.Connection.Delete()

        new_connection_setting = {
            'ipv4': {
                'method': 'auto'
            },
            'connection': {'id': ifname,
                           'type': '802-3-ethernet',
                           'interface-name': ifname,
                           'uuid': str(uuid.uuid4())}
        }

        NetworkManager.Settings.AddConnection(new_connection_setting)


    def static(self, ifname, ip, netmask=24, gateway="0.0.0.0", dns1=None, dns2=None, dns3=None):
        """ Set network interface to static
        Args:
            ifname(str): Interface name :func=["network", "list"]
            ip(str): IP address
            netmask(int): Netmask
            gateway(str): Gateway
            dns1(str): Nameserver1
            dns2(str): Nameserver2
            dns3(str): Nameserver3
        Raises:
            NameError(str): ifname invalid
            ValueError(str): ip, gateway or dns invalid
        """
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise ValueError("ip: %s is invalid" % ip)

        if gateway:
            try:
                ipaddress.ip_address(gateway)
            except ValueError:
                raise ValueError("gateway: %s is invalid" % gateway)

        dev = get_device(ifname)
        if dev is None:
            raise NameError('no such interface', ifname)

        dev.ActiveConnection.Connection.Delete()

        new_connection_setting = {
            'ipv4': {
                'method': 'manual',
                'addresses': [(ip, netmask, gateway)]
            },
            'connection': {'id': ifname,
                           'type': '802-3-ethernet',
                           'interface-name': ifname,
                           'uuid': str(uuid.uuid4())}
        }

        NetworkManager.Settings.AddConnection(new_connection_setting)

