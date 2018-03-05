from nas.utils.command import exec_command
from larva.core import LarvaObject
import json
from collections import OrderedDict
import pwd
import crypt

class User(LarvaObject):

    def __init__(self):
        pass

    def _start(self):
        pass

    def list(self, all=False):
        """ List all users
       Returns:
            user_list(dict): a list of user
        """
        users = pwd.getpwall()
        output = OrderedDict()
        for user in users:
            name, passwd, uid, gid, gecos, dir, shell = user
            if all or not (uid > 999 and uid < 65534):
                continue
            output[name] = OrderedDict()
            output[name]['uid'] = uid
            output[name]['gid'] = gid
            output[name]['dir'] = dir
            output[name]['shell'] = shell


        return output

    def create(self, username, password):
        """ Create user
        Args:
            username(str): User name
            password(str): Password
        Raises:
            NameError(str): Username error
            ParameterError(str): Password error
        """

        try:
            exec_command('id %s' % username)
            raise NameError('User %s already exists' % username)
        except:
            pass

        encrypted_passwd = crypt.crypt(password, crypt.mksalt(crypt.METHOD_MD5))
        exec_command("adduser -D -H -h {} -s {} -G users {} ".format('/', '/bin/false', username))
        exec_command("echo {}:{} | chpasswd".format(username, encrypted_passwd))
        exec_command("printf '{}\n{}\n' | smbpasswd -a -s {}".format(password, password, username))

    def destroy(self, username):
        """ Destroy user
        Args:
            username(str): User name:func=["user", "list"]
        Raises:
            NameError(str): Can not delete admin
        """
        if username == 'admin':
            raise NameError('Can not delete admin')
        exec_command('deluser %s' % username)

    def chpasswd(self, username, password):
        """ Change password
        Args:
            username(str): User name
            password(str): Password
        Raises:
            NameError(str): username error
        """
        try:
            exec_command('id %s' % username)
        except:
            raise NameError('User %s not exists' % username)

        encrypted_passwd = crypt.crypt(password, crypt.mksalt(crypt.METHOD_MD5))
        exec_command("echo {}:{} | chpasswd".format(username, encrypted_passwd))