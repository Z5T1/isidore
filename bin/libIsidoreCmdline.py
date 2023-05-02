#!/usr/bin/env python3

from libIsidore import *

class IsidoreCmdline:

    isidore = None

    def __init__(self, isidore):
        self.isidore = isidore

    # > ?
    def help(self, args):
        print('''\
?           print this help message
create      create various objects (such as hosts and tags)
echo        print text back to the console
help        alias for ?
host        manipulate a host
quit        exit
show        print various data
tag         manipulate a tag''')

    # > show
    def show(self, args):
        if len(args) == 1 or args[1] == '?':
            print('''\
?           print this help message
hosts       print all hosts in the database
inventory   print the full Ansible inventory file
tag         print all tags in the database''')

        elif args[1] == 'hosts':
            self.show_hosts(args[1:])

    # > show hosts
    def show_hosts(self, args):
        for host in self.isidore.getHosts():
            print(host.getHostname())

