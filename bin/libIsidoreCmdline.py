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
end         go back to the previous prompt
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
hosts       print all commissioned hosts in the database
graveyard   print all decommissioned hosts in the database
inventory   print the full Ansible inventory file
tags        print all tags in the database''')

        elif args[1] == 'hosts':
            self.show_hosts(args[1])

        elif args[1] == 'graveyard':
            self.show_graveyard(args[1])

        elif args[1] == 'tags':
            self.show_tags(args[1])

    # > show hosts
    def show_hosts(self, args):
        for host in self.isidore.getCommissionedHosts():
            print(host.getHostname())

    # > show graveyard
    def show_graveyard(self, args):
        for host in self.isidore.getDecommissionedHosts():
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
show        display host attributes
tag         display and modify this host's tags''')
        elif args[2] == 'set':
            self.host_set(args)
        elif args[2] == 'show':
            self.host_show(args)
        elif args[2] == 'tag':
            self.host_tag(args)

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
                "\\'")+"'")
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
            self.host_set_commissioned(args)
        elif args[3] == 'decommissioned':
            self.host_set_decommissioned(args)
        elif args[3] == 'description':
            if len(args) == 4:
                print("<description>   the description")
            else:
                host.setDescription(args[4])

    # > host <hostname> set commissioned
    def host_set_commissioned(self, args):
        host = self.isidore.getHost(args[1])
        if len(args) == 4:
            self.subprompt(args, self.host)
        elif args[4] == '?':
            print('''\
<date>      the commission date
now         use the current date''')
        elif args[4] == 'now':
            host.setCommissionDate(datetime.datetime.now())
        else:
            try:
                host.setCommissionDate(args[4])
            except:
                print("Failed to set commission date")

    # > host <hostname> set decommissioned
    def host_set_decommissioned(self, args):
        host = self.isidore.getHost(args[1])
        if len(args) == 4:
            self.subprompt(args, self.host)
        elif args[4] == '?':
            print('''\
<date>      the decommission date
never       clear the decommission date
now         use the current date''')
        elif args[4] == 'never':
            host.setDecommissionDate(None)
        elif args[4] == 'now':
            host.setDecommissionDate(datetime.datetime.now())
        else:
            try:
                host.setDecommissionDate(args[4])
            except:
                print("Failed to set decommission date")

    # > host <hostname> tag
    def host_tag(self, args):
        host = self.isidore.getHost(args[1])
        if len(args) == 3:
            self.subprompt(args, self.host)
        elif args[3] == '?':
            print('''\
?           print this help message
add         add a tag to this host
list        list the tags currently assigned to this host
list-detail display a detailed list of tags currently assigned to this host
remove      remove a tag from this host''')

        elif args[3] == 'add':
            if len(args) == 4:
                print("<tag>           name of the tag to add")
                return
            tag = self.isidore.getTag(args[4])
            if tag == None:
                print("Tag "+args[4]+" does not exist")
                return
            try:
                host.addTag(tag)
            except:
                print(traceback.format_exc(),
                        file=sys.stderr)

        elif args[3] == 'list':
            for tag in host.getTags():
                print(tag.getName())

        elif args[3] == 'list-detail':
            print("Name\t\tGroup\t\tDescription")
            for tag in host.getTags():
                print(tag.getName()+"\t"+tag.getGroup()+"\t\t"+tag.getDescription())

        elif args[3] == 'remove':
            if len(args) == 4:
                print("<tag>           name of the tag to remove")
                return
            tag = self.isidore.getTag(args[4])
            if tag == None:
                print("Tag "+args[4]+" does not exist")
                return
            host.removeTag(tag)

    # > tag
    def tag(self, args):
        if len(args) == 1:
            self.subprompt(args, self.tag)
        elif args[1] == '?':
            print('''\
?           print this help message
<tagname>  the name of the tag to edit''')
        elif len(args) == 2:
            self.subprompt(args, self.tag)
        elif args[2] == '?':
            print('''\
?           print this help message
host        display and modify hosts that have this tag
set         modify tag attributes
show        display tag attributes''')
        elif args[2] == 'host':
            self.tag_host(args)
        elif args[2] == 'set':
            self.tag_set(args)
        elif args[2] == 'show':
            self.tag_show(args)

    # > tag <tagname> host
    def tag_host(self, args):
        tag = self.isidore.getTag(args[1])
        if len(args) == 3:
            self.subprompt(args, self.tag)
        elif args[3] == '?':
            print('''\
?           print this help message
list        display all hosts that have this tag''')
        elif args[3] == 'list':
            for host in tag.getHosts():
                print(host.getHostname())

    # > tag <tagname> show
    def tag_show(self, args):
        tag = self.isidore.getTag(args[1])
        if len(args) == 3:
            self.subprompt(args, self.tag)
        elif args[3] == '?':
            print('''\
?           print this help message
all         print all the information about the tag
description     print the tag's description
group       print the date the tag was commissioned''')
        elif args[3] == 'all':
            print(
            tag.getName()+":\n"
            "  group: '"+str(tag.getGroup()).replace("'",
                "\\'")+"'\n"
            "  description: '"+tag.getDescription().replace("'",
                "\\'")+"'")
        elif args[3] == 'description':
            print(tag.getDescription())
        elif args[3] == 'group':
            print(tag.getGroup())

    # > tag <tagname> set
    def tag_set(self, args):
        tag = self.isidore.getTag(args[1])
        if len(args) == 3:
            self.subprompt(args, self.tag)
        elif args[3] == '?':
            print('''\
?           print this help message
description     set the tag's description
group           set the tag's group''')
        elif args[3] == 'group':
            self.tag_set_group(args)
        elif args[3] == 'description':
            if len(args) == 4:
                print("<description>   the description")
            else:
                tag.setDescription(args[4])

    # > tag <tagname> set group
    def tag_set_group(self, args):
        tag = self.isidore.getTag(args[1])
        if len(args) == 4:
            self.subprompt(args, self.tag)
        elif args[4] == '?':
            print('''\
<group>     the tag group''')
        elif args[4] == 'none':
            tag.setGroup(None)
        else:
            try:
                tag.setGroup(args[4])
            except:
                print("Failed to set group")

