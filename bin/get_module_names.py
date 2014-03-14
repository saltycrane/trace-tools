"""
From http://stackoverflow.com/a/6464112/101911
"""
import distutils.sysconfig as sysconfig
import os
from pprint import pprint

std_lib = sysconfig.get_python_lib(standard_lib=True)

module_list = []
for top, dirs, files in os.walk(std_lib):
    for nm in files:
        if nm != '__init__.py' and nm[-3:] == '.py':
            module_path = os.path.join(top, nm)[len(std_lib) + 1:-3].replace('\\', '.')
            if module_path.startswith('dist-packages'):
                continue
            if module_path.startswith('site-packages'):
                continue

            module_path = module_path.replace('/', '.')
            module_list.append(module_path)

module_list = list(set(module_list))
module_list = sorted(module_list)
pprint(module_list)
