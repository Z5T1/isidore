#!/usr/bin/env python3

import shlex
import sys
import traceback
import datetime

from libIsidore import *

class IsidoreCmdline:

    isidore = None

    def __init__(self, isidore):
        self.isidore = isidore

    # Start a subprompt.
    # @param prompt     The existing arguments to display at the
    #                   prompt and prepend to read command
    #                   arguments before passing to func.
    # @param func       The function to use to process input from
    #                   the subprompt.
    def subprompt(self, prompt, func):
        line = []
        while line != ['end']:
            try:
                line = shlex.split(input(' '.join(prompt) + '> '))
            except EOFError:
                print()
                return

            if line == []:
                continue
            elif line == ['end']:
                return
            elif line == ['quit']:
                exit()
            elif line[0] == '?':
                print('''\
^D          alias for end
end         go back one prompt level
quit        exit''')

            func(prompt + line)

    # Start an interactive prompt
    def prompt(self):
        self.subprompt([], self.rootprompt)

    # >
    def rootprompt(self, args):

        # Parse inut
        if args[0] == '?':
            self.help(args)
        if args[0] == 'create':
            self.create(args)
        if args[0] == 'echo':
            self.echo(args)
        if args[0] == 'help':
            print('''\
Pst! You should really use ? to display the help message. ? will
work at every subprompt level. help only works at the root
prompt.
''')
            self.help(args)
        if args[0] == 'host':
            self.host(args)
        if args[0] == 'show':
            self.show(args)
        if args[0] == 'tag':
            self.tag(args)

    # > ?
    def help(self, args):
        print('''\
?           print this help message
create      create various objects (such as hosts and tags)
echo        print text back to the console
help        alias for ?
host        manipulate a host
show        print various data
tag         manipulate a tag''')

    # > show
    def show(self, args):
        if len(args) == 1:
            self.subprompt(args, self.show)

        elif args[1] == '?':
            print('''\
?           print this help message
hosts       print all hosts in the database
inventory   print the full Ansible inventory file
tags        print all tags in the database''')

        elif args[1] == 'hosts':
            self.show_hosts(args[1:])

        elif args[1] == 'tags':
            self.show_tags(args[1:])

    # > show hosts
    def show_hosts(self, args):
        for host in self.isidore.getHosts():
            print(host.getHostname())

    # > show tags
    def show_tags(self, args):
        for tag in self.isidore.getTags():
            print(tag.getName())

    # > create
    def create(self, args):
        if len(args) == 1:
            self.subprompt(args, self.create)
        elif args[1] == '?':
            print('''\
?           print this help message
host        create a new host
tag         create a new tag''')
        elif args[1] == 'host':
            self.create_host(args)
        elif args[1] == 'tag':
            self.create_tag(args)

    # > create host
    def create_host(self, args):
        if len(args) == 2:
            self.subprompt(args, self.create)
        elif args[2] == '?':
            print('''\
?           print this help message
<hostname>  the hostname for the new host to create''')
        else:
            try:
                self.isidore.createHost(args[2])
            except:
                print('Failed to create host '+args[2],
                        file=sys.stderr)
                print(traceback.format_exc(),
                        file=sys.stderr)

    # > create tag
    def create_tag(self, args):
        if len(args) == 2:
            self.subprompt(args, self.create)
        elif args[2] == '?':
            print('''\
?           print this help message
<name>      the name of the new tag to create''')
        else:
            try:
                self.isidore.createTag(args[2])
            except:
                print('Failed to create tag '+args[2],
                        file=sys.stderr)
                print(traceback.format_exc(),
                        file=sys.stderr)

    # > echo
    def echo(self, args):
        if len(args) == 1:
            self.subprompt(args, self.echo)
        elif args[1] == '?':
            print('''\
?           print this help message
<text>      text to print''')
        else:
            print(' '.join(args[1:]))

    # > host
    def host(self, args):
        if len(args) == 1:
            self.subprompt(args, self.host)
        elif args[1] == '?':
            print('''\
?           print this help message
<hostname>  the name of the host to edit''')
        elif len(args) == 2:
            self.subprompt(args, self.host)
        elif args[2] == '?':
            print('''\
?           print this help message
set         modify host attributes
show        display information about this host''')
        elif args[2] == 'set':
            self.host_set(args)
        elif args[2] == 'show':
            self.host_show(args)

    # > host <hostname> show
    def host_show(self, args):
        host = self.isidore.getHost(args[1])
        if len(args) == 3:
            self.subprompt(args, self.host)
        elif args[3] == '?':
            print('''\
?           print this help message
all         print all the information about the host
commissioned    print the date the host was commissioned
description     print the host's description
decommissioned  print the date the host was decommissioned''')
        elif args[3] == 'all':
            print(
            host.getHostname()+":\n"
            "  commissioned: '"+str(host.getCommissionDate())+"'\n"
            "  decommissioned: '"+str(host.getDecommissionDate())+"'\n"
            "  description: '"+host.getDescription().replace("'",
                "\\'"))
        elif args[3] == 'commissioned':
            print(host.getCommissionDate())
        elif args[3] == 'description':
            print(host.getDescription())
        elif args[3] == 'decommissioned':
            print(host.getDecommissionDate())

    # > host <hostname> set
    def host_set(self, args):
        host = self.isidore.getHost(args[1])
        if len(args) == 3:
            self.subprompt(args, self.host)
        elif args[3] == '?':
            print('''\
?           print this help message
commissioned    set the date the host was commissioned
description     set the host's description
decommissioned  set the date the host was decommissioned''')
        elif args[3] == 'commissioned':
            if len(args) == 4:
                print("<date>          the commission date")
            else:
                host.setCommissionDate(args[4])
        elif args[3] == 'decommissioned':
            if len(args) == 4:
                print("<date>          the decommission date")
            else:
                host.setDecommissionDate(args[4])
        elif args[3] == 'description':
            if len(args) == 4:
                print("<description>   the description")
            else:
                host.setDescription(args[4])

