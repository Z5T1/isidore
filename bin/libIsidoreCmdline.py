#!/usr/bin/env python3

import shlex
import sys
import traceback

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
quit        exit
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

