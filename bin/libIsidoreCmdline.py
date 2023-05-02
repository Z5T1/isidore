#!/usr/bin/env python3

import shlex

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

            if line == ['quit']:
                exit()
            elif line[0] == '?':
                print('''\
end         Go back one prompt level
quit        exit''')

            func(prompt + line)

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

