import os
import sys
import glob
import uuid
import inspect
import importlib
from larva.core import Larva
from larva.auth import Auth
from larva.core import LarvaObject
from nas.utils.command import exec_command
from werkzeug.contrib.fixers import ProxyFix


# Add default admin session
auth = Auth()
if 'admin' not in auth.users_db:
    uid = str(uuid.uuid4())
    auth.users_db["admin"] = uid
    auth.token_db[uid] = "admin"
    auth.users_db.save()
    auth.token_db.save()


def get_module_list():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    modules_dir = os.path.join(this_dir, 'modules')

    module_list = list()
    module_files = glob.glob(modules_dir+"/[a-z]*.py")
    for file in module_files:
        module_name = os.path.basename(file).split('.')[0]
        m = importlib.import_module("nas.modules.%s" % module_name)
        module_attrs = dir(m)
        for attr_name in module_attrs:
            attr = getattr(m, attr_name)
            if inspect.isclass(attr) and issubclass(attr, LarvaObject) and attr != LarvaObject:
                module_list.append(attr)
    return module_list

modules = get_module_list()
server = Larva(modules, host='0.0.0.0', port=8080, auth=auth)
app = server.app

exec_command("chmod 660 /var/db/larva.db")
exec_command("chown root:admin /var/db/larva.db")
app.wsgi_app = ProxyFix(app.wsgi_app)

