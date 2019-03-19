import re


class Class:
    def __init__(self, class_name, body):
        self.class_name = class_name
        self.body = body


with open('./controller_old.py', 'r') as fin:
    grouped_classes = {}
    class_groups = dict(zip(
        'API, Compute, Controller, Struct, Graphics, Nodes, Project, VM'.split(', '),
        [[x] for x in 'GNS3API, GNS3Compute, GNS3Controller, Struct'.split(', ')] +
        [
            'GNS3Drawing, GNS3Image'.split(', '),
            'GNS3Node, GNS3NodePort, GNS3NodeProperties, GNS3Link'.split(', '),
            'GNS3Project, GNS3Snapshot'.split(', '),
            'GNS3VM, GNS3VMEngine'.split(', '),
        ]
    ))

    for grp in class_groups.items(): print(grp)

    current_class = None
    for ind, line in enumerate(fin.readlines()):
        if line[:5] == 'class':
            if current_class is not None:
                # print(class_groups)
                for cls_group, classes in class_groups.items():
                    if current_class.class_name in classes:
                        if cls_group in grouped_classes.keys():
                            grouped_classes[cls_group].append(current_class)
                        else:
                            grouped_classes[cls_group] = [current_class]

            current_class = Class(class_name=line.split()[1][:-1], body=[line])
            print(current_class.class_name)

        elif line[0].isalpha():
            if current_class is not None:
                for cls_group, classes in class_groups.items():
                    if current_class.class_name in classes:
                        if cls_group in grouped_classes.keys():
                            grouped_classes[cls_group].append(current_class)
                        else:
                            grouped_classes[cls_group] = [current_class]

            current_class = None

        else:
            if current_class is not None:
                current_class.body.append(line)

    print('---------------')
    for k, cls in grouped_classes.items():
        print('Class: ', k, [x.class_name for x in cls])
    print('---------------')
    for cls in class_groups.items():
        pass
        # print(cls)

    for group_name, group_classes in class_groups.items():
        print(group_name)
        print('-' * 50)
        with open(f'./{group_name}.py', 'w') as group_out:
            file_content = ''.join([''.join(c.body) for c in grouped_classes[group_name]])

            # other_modules = [x for x in class_groups.values() for y in x if y not in group_classes]
            other_modules = {mod for mod, mod_classes in class_groups.items() for cls in mod_classes if
                             cls not in group_classes}

            print(other_modules)

            preamble = []
            print(group_name, other_modules)

            for mod in other_modules:
                res = False
                for contained_cls in grouped_classes[mod]:
                    if [m.start() for m in
                        re.finditer(r'[\wa-zA-Z\.]?' + contained_cls.class_name + r'[\w\(\)\.][\w\)*]', file_content)]:
                        res = True
                if res:
                    preamble.append(mod)

            group_out.write('''import json
import platform
from configparser import ConfigParser
from pathlib import Path
from requests import delete, get, post
from requests.auth import HTTPBasicAuth
import os
import sys
''')

            for p in preamble:
                group_out.write(f'from pygns3.{p} import *\n')

            print('Preamble: ', preamble)

            group_out.write(file_content)
            # print(file_content)
