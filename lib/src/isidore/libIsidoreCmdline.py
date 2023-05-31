#!/usr/bin/env python3

# Copyright © 2023 Scott Court
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the “Software”), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import shlex
import sys
import traceback
import datetime

from isidore.libIsidore import *

# The Isidore command prompt
class IsidoreCmdline:

    _isidore = None
    _version = '0.1.5'

    # Creates a new Isidore command prompt
    # @param isidore    The underlying Isidore instance for the command prompt
    #                   to connect to.
    def __init__(self, isidore):
        self._isidore = isidore

    # Gets the Isidore Command Prompt version
    # @return       The Isidore Command Prompt version
    def getVersion(self):
        return self._version

    # Start a subprompt.
    # @param prompt     The existing arguments to display at the
    #                   prompt and prepend to read command
    #                   arguments before passing to func.
    # @param func       The function to use to process input from
    #                   the subprompt.
    def subprompt(self, prompt, func):
        line = []
        while line != ['end']:
            # Determine prompt
            if sys.stdin.isatty():
                display_prompt = ' '.join(prompt) + '> '
            else:
                display_prompt = ''

            # Read input
            try:
                line = shlex.split(input(display_prompt))
            except EOFError:
                print()
                return
            except KeyboardInterrupt:
                print('^C')
                continue
            except:
                print("Malformed command", file=sys.stderr)
                continue

            # Process input
            if line == []:
                continue
            elif line == ['end']:
                return
            elif line == ['quit']:
                exit()
            elif line[0] == '?':
                print('''\
^C          clear the current command
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
        elif args[0] == 'create':
            self.create(args)
        elif args[0] == 'delete':
            self.delete(args)
        elif args[0] == 'describe':
            self.describe(args)
        elif args[0] == 'echo':
            self.echo(args)
        elif args[0] == 'help':
            print('''\
Pst! You should really use ? to display the help message. ? will
work at every subprompt level. help only works at the root
prompt.
''')
            self.help(args)
        elif args[0] == 'host':
            self.host(args)
        elif args[0] == 'rename':
            self.rename(args)
        elif args[0] == 'show':
            self.show(args)
        elif args[0] == 'tag':
            self.tag(args)
        elif args[0] == 'version':
            self.version(args)
        else:
            print('Invalid command '+args[0]+'. Enter ? for help.', file=sys.stderr)

    # > ?
    def help(self, args):
        print('''\
?           print this help message
create      create various objects (such as hosts and tags)
delete      delete various objects (such as hosts and tags)
describe    print details about various data
echo        print text back to the console
help        alias for ?
host        manipulate a host
rename      rename various objects (such as hosts and tags)
show        print various data
tag         manipulate a tag
version     display Isidore version information''')

    # > show
    def show(self, args):
        if len(args) == 1:
            self.subprompt(args, self.show)

        elif args[1] == '?':
            print('''\
?           print this help message
config      print the commmands to populate the database with the current 
            configuration
hosts       print all commissioned hosts in the database
graveyard   print all decommissioned hosts in the database
inventory   print the full Ansible inventory file
tag-groups  print all the tag groups in the database
tags        print all tags in the database''')

        elif args[1] == 'config':
            self.show_config(args[1])

        elif args[1] == 'hosts':
            self.show_hosts(args[1])

        elif args[1] == 'inventory':
            self.show_inventory(args)

        elif args[1] == 'graveyard':
            self.show_graveyard(args[1])

        elif args[1] == 'tag-groups':
            self.show_taggroups(args[1])

        elif args[1] == 'tags':
            self.show_tags(args[1])

        else:
            print('Invalid argument '+args[1]+'. Enter ? for help.', file=sys.stderr)

    # > show config
    def show_config(self, args):
        hosts = self._isidore.getHosts()
        tags = self._isidore.getTags()

        # Create Hosts
        for host in hosts:
            name = "'"+host.getHostname().replace("'", "'\"'\"'")+"'"
            print("create host "+name)
            print("host "+name+" set commissioned '"+\
                    str(host.getCommissionDate())+"'")
            print("host "+name+" set decommissioned '"+\
                    str(host.getDecommissionDate()).lower()+"'")
            if host.getDescription() == None:
                print("host "+name+" set description none")
            else:
                print("host "+name+" set description '"+\
                        str(host.getDescription()).replace("'", "'\"'\"'")+"'")
            print("host "+name+" var set $ '"+\
                    json.dumps(host.getVar()).replace("'", "'\"'\"'")+"'")
        print()

        # Create Tags
        for tag in tags:
            name = "'"+tag.getName().replace("'", "'\"'\"'")+"'"
            group = tag.getGroup()
            description = tag.getDescription()
            print("create tag %s" % (name))
            print("tag %s set group '%s'" %
                    (name,
                    'none' if group == None
                        else group.replace("'", "'\"'\"'")))
            print("tag %s set description '%s'" % 
                    (name,
                    'none' if description == None
                        else description.replace("'", "'\"'\"'")))
            print("tag "+name+" var set $ '"+\
                    json.dumps(tag.getVar()).replace("'", "'\"'\"'")+"'")
        print()

        # Assign Tags to Hosts
        for host in hosts:
            hostname = "'"+host.getHostname().replace("'", "'\"'\"'")+"'"
            for tag in host.getTags():
                print("host "+hostname+" tag add '"+\
                        str(tag.getName()).replace("'", "'\"'\"'")+"'")

    # > show graveyard
    def show_graveyard(self, args):
        for host in self._isidore.getDecommissionedHosts():
            print(host.getHostname())

    # > show hosts
    def show_hosts(self, args):
        for host in self._isidore.getCommissionedHosts():
            print(host.getHostname())

    # > show inventory
    def show_inventory(self, args):
        if len(args) == 2:
            print(self._isidore.getInventoryIni())

        elif args[2] == '?':
            print('''\
?           print this help message
human       print the inventory in a human friendly format
ini         print the inventory in INI format
json        print the inventory in JSON format
yaml        print the inventory in YAML format''')

        elif args[2] == 'human':
            print(yaml.dump(self._isidore.getInventory(), default_flow_style=False))
        elif args[2] == 'ini':
            print(self._isidore.getInventoryIni())
        elif args[2] == 'json':
            print(self._isidore.getInventoryJson())
        elif args[2] == 'yaml':
            print(self._isidore.getInventoryYaml())
        else:
            print('Invalid format '+args[2]+'. Enter ? for help.', file=sys.stderr)

    # > show tag-groups
    def show_taggroups(self, args):
        tags = {}

        # Populate the top level
        for (group, tagsstr) in self._isidore.getTagGroups():
            if group == None:
                group = 'ungrouped'
            tags[group] = list()

        for tag in self._isidore.getTags():
            group = tag.getGroup()
            if group == None:
                group = 'ungrouped'
            tags[group].append(tag.getName())

        print(yaml.dump(tags, default_flow_style=False))

    # > show tags
    def show_tags(self, args):
        for tag in self._isidore.getTags():
            print(tag.getName())

    # > describe
    def describe(self, args):
        if len(args) == 1:
            self.subprompt(args, self.describe)

        elif args[1] == '?':
            print('''\
?           print this help message
hosts       describe all commissioned hosts in the database
graveyard   describe all decommissioned hosts in the database
tag-groups  describe all the tag groups in the database
tags        describe all tags in the database''')

        elif args[1] == 'hosts':
            self.describe_hosts(args[1])

        elif args[1] == 'graveyard':
            self.describe_graveyard(args[1])

        elif args[1] == 'tag-groups':
            self.describe_taggroups(args[1])

        elif args[1] == 'tags':
            self.describe_tags(args[1])

        else:
            print('Invalid argument '+args[1]+'. Enter ? for help.', file=sys.stderr)

    # > describe hosts
    def describe_hosts(self, args):
        hosts = {}
        for host in self._isidore.getCommissionedHosts():
            hosts[host.getHostname()] = host.getDescription()
        print(yaml.dump(hosts, default_flow_style=False))

    # > describe graveyard
    def describe_graveyard(self, args):
        hosts = {}
        for host in self._isidore.getDecommissionedHosts():
            hosts[host.getHostname()] = host.getDescription()
        print(yaml.dump(hosts, default_flow_style=False))


    # > describe tag-groups
    def describe_taggroups(self, args):
        tags = {}

        # Populate the top level
        for (group, tagsstr) in self._isidore.getTagGroups():
            if group == None:
                group = 'ungrouped'
            tags[group] = list()

        for tag in self._isidore.getTags():
            group = tag.getGroup()
            if group == None:
                group = 'ungrouped'
            tags[group].append( { tag.getName(): tag.getDescription() } )

        print(yaml.dump(tags, default_flow_style=False))

    # > describe tags
    def describe_tags(self, args):
        tags = {}
        for tag in self._isidore.getTags():
            tags[tag.getName()] = tag.getDescription()
        print(yaml.dump(tags, default_flow_style=False))

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
        else:
            print('Invalid argument '+args[1]+'. Enter ? for help.', file=sys.stderr)

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
                self._isidore.createHost(args[2])
            except mysql.connector.errors.IntegrityError as e:
                print('Host %s already exists' % args[2],
                        file=sys.stderr)
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
                self._isidore.createTag(args[2])
            except mysql.connector.errors.IntegrityError as e:
                print('Tag %s already exists' % args[2],
                        file=sys.stderr)
            except:
                print('Failed to create tag '+args[2],
                        file=sys.stderr)
                print(traceback.format_exc(),
                        file=sys.stderr)

    # > delete
    def delete(self, args):
        if len(args) == 1:
            self.subprompt(args, self.delete)
        elif args[1] == '?':
            print('''\
?           print this help message
host        delete a host
tag         delete a tag''')
        elif args[1] == 'host':
            self.delete_host(args)
        elif args[1] == 'tag':
            self.delete_tag(args)
        else:
            print('Invalid argument '+args[1]+'. Enter ? for help.', file=sys.stderr)

    # > delete host
    def delete_host(self, args):
        if len(args) == 2:
            self.subprompt(args, self.delete_host)
            return
        elif args[2] == '?':
            print('''\
?           print this help message
<hostname>  the hostname of the host to delete''')
            return

        host = self._isidore.getHost(args[2])
        if host == None:
            print('Host '+args[2]+' does not exist!')
            return

        try:
            host.delete()
            print("Host "+args[2]+" has been deleted.")
        except mysql.connector.Error as e:
            if e.errno == 1451:
                print("Cannot delete host "+host.getHostname()+": it still has tags assigned to it.", file=sys.stderr)
            else:
                print('Failed to delete host '+args[2],
                        file=sys.stderr)
                print(traceback.format_exc(),
                        file=sys.stderr)
        except:
            print('Failed to delete host '+args[2],
                    file=sys.stderr)
            print(traceback.format_exc(),
                    file=sys.stderr)

    # > delete tag
    def delete_tag(self, args):
        if len(args) == 2:
            self.subprompt(args, self.delete_tag)
            return
        elif args[2] == '?':
            print('''\
?           print this help message
<name>      the name of the tag to delete''')
            return

        tag = self._isidore.getTag(args[2])
        if tag == None:
            print('Tag '+args[2]+' does not exist!')
            return

        try:
            tag.delete()
            print("Tag "+args[2]+" has been deleted.")
        except mysql.connector.Error as e:
            if e.errno == 1451:
                print("Cannot delete tag "+tag.getName()+": it still has hosts assigned to it.", file=sys.stderr)
            else:
                print('Failed to delete tag '+args[2],
                        file=sys.stderr)
                print(traceback.format_exc(),
                        file=sys.stderr)
        except:
            print('Failed to delete tag '+args[2],
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
        # Handle arg #1 (host <ARG1>)
        if len(args) == 1:
            self.subprompt(args, self.host)
            return
        elif args[1] == '?':
            print('''\
?           print this help message
<hostname>  the name of the host to edit''')
            return
        host = self._isidore.getHost(args[1])
        if host == None:
            print('Host '+args[1]+' does not exist!')
            return

        # Handle arg #2 (host foo <ARG2>)
        elif len(args) == 2:
            self.subprompt(args, self.host)
        elif args[2] == '?':
            print('''\
?           print this help message
describe    print details about host attributes
set         modify host attributes
show        display host attributes
tag         display and modify this host's tags
var         display and modify this host's variables''')
        elif args[2] == 'describe':
            self.host_describe(args)
        elif args[2] == 'set':
            self.host_set(args)
        elif args[2] == 'show':
            self.host_show(args)
        elif args[2] == 'tag':
            self.host_tag(args)
        elif args[2] == 'var':
            self.host_var(args)
        else:
            print('Invalid command '+args[2]+'. Enter ? for help.', file=sys.stderr)

    # > host <hostname> describe
    def host_describe(self, args):
        host = self._isidore.getHost(args[1])
        if len(args) == 3:
            self.subprompt(args, self.host_describe)
        elif args[3] == '?':
            print('''\
?           print this help message
tags        describe the tags currently assigned to this host''')
        elif args[3] == 'tags':
            tags = {}
            for tag in host.getTags():
                tags[tag.getName()] = tag.getDescription()
            print(yaml.dump(tags, default_flow_style=False))
        else:
            print('Invalid argument '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > host <hostname> show
    def host_show(self, args):
        host = self._isidore.getHost(args[1])
        if len(args) == 3:
            self.subprompt(args, self.host)
        elif args[3] == '?':
            print('''\
?           print this help message
all         print all the information about the host
commissioned    print the date the host was commissioned
description     print the host's description
decommissioned  print the date the host was decommissioned
tags        print the tags currently assigned to this host''')
        elif args[3] == 'all':
            print(yaml.dump(host.getDetails(), default_flow_style=False))
        elif args[3] == 'commissioned':
            print(host.getCommissionDate())
        elif args[3] == 'description':
            print(host.getDescription())
        elif args[3] == 'decommissioned':
            print(host.getDecommissionDate())
        elif args[3] == 'tags':
            for tag in host.getTags():
                print(tag.getName())
        else:
            print('Invalid argument '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > host <hostname> set
    def host_set(self, args):
        host = self._isidore.getHost(args[1])
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
            elif args[4] == 'none':
                host.setDescription(None)
            else:
                host.setDescription(args[4])
        else:
            print('Invalid argument '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > host <hostname> set commissioned
    def host_set_commissioned(self, args):
        host = self._isidore.getHost(args[1])
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
        host = self._isidore.getHost(args[1])
        if len(args) == 4:
            self.subprompt(args, self.host)
        elif args[4] == '?':
            print('''\
<date>      the decommission date
none        clear the decommission date
now         use the current date''')
        elif args[4] == 'none':
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
        host = self._isidore.getHost(args[1])
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
            self.host_tag_add(args)

        elif args[3] == 'list':
            for tag in host.getTags():
                print(tag.getName())

        elif args[3] == 'list-detail':
            tags = list()
            for tag in host.getTags(True):
                tags.append( {
                    'name': tag.getName(),
                    'group': tag.getGroup(),
                    'description': tag.getDescription()
                    } )
            print(yaml.dump(tags, default_flow_style=False, sort_keys=False))

        elif args[3] == 'remove':
            self.host_tag_remove(args)
        else:
            print('Invalid command '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > host <hostname> var
    def host_var(self, args):
        host = self._isidore.getHost(args[1])
        if len(args) == 3:
            self.subprompt(args, self.host_var)
        elif args[3] == '?':
            print('''\
?           print this help message
append      append a value to a list variable
print       print a variable
set         set a variable
unset       unset (delete) a variable''')

        elif args[3] == 'append':
            self.host_var_append(args)

        elif args[3] == 'print':
            if len(args) == 4:
                print(yaml.dump(
                    host.getVar(),
                    default_flow_style=False,
                    sort_keys=False))
            elif args[4] == '?':
                print('''\
?           print this help message
$           print all variables
<variable>  name of the variable to print''')
            else:
                print(yaml.dump(
                    host.getVar(args[4]),
                    default_flow_style=False,
                    sort_keys=False))

        elif args[3] == 'set':
            self.host_var_set(args)

        elif args[3] == 'unset':
            self.host_var_unset(args)

        else:
            print('Invalid command '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > host <hostname> var append
    def host_var_append(self, args):
        host = self._isidore.getHost(args[1])
        if len(args) == 4:
            self.subprompt(args, self.host_var_append)
        elif args[4] == '?':
            print('''\
?           print this help message
<variable>  name of the list variable to append to''')

        elif len(args) == 5:
            self.subprompt(args, self.host_var_append)

        elif args[5] == '?':
            print('''\
?           print this help message
<json>      the JSON value to append to the list''')

        else:
            try:
                host.appendVar(args[4], json.loads(args[5]))
            except json.decoder.JSONDecodeError:
                print(args[5] + '''
^-- this is not valid JSON

Strings must be double quoted. It will be necessary to either nest double
quotes inside single quotes or escape the double quotes like so:

   > host myhost var set foo '"bar"'

or

   > host myhost var set foo \\"bar\\"

''')
            except:
                print(\
'Failed to append to list variable. Is %s a valid list path?' % args[4])

    # > host <hostname> var set
    def host_var_set(self, args):
        host = self._isidore.getHost(args[1])
        if len(args) == 4:
            self.subprompt(args, self.host_var_set)
        elif args[4] == '?':
            print('''\
?           print this help message
$           set/replace the entire variable tree
<variable>  name of the variable to set''')

        elif len(args) == 5:
            self.subprompt(args, self.host_var_set)

        elif args[5] == '?':
            print('''\
?           print this help message
<json>      the JSON value to set the variable to''')

        else:
            try:
                host.setVar(args[4], json.loads(args[5]))
            except json.decoder.JSONDecodeError:
                print(args[5] + '''
^-- this is not valid JSON

Strings must be double quoted. It will be necessary to either nest double
quotes inside single quotes or escape the double quotes like so:

   > host myhost var set foo '"bar"'

or

   > host myhost var set foo \\"bar\\"

''')

    # > host <hostname> var unset
    def host_var_unset(self, args):
        host = self._isidore.getHost(args[1])
        if len(args) == 4:
            self.subprompt(args, self.host_var_set)
        elif args[4] == '?':
            print('''\
?           print this help message
<variable>  name of the variable to unset''')
        else:
            try:
                host.unsetVar(args[4])
            except:
                print("Failed to unset variable %s" % args[4])

    # > host <hostname> tag add
    def host_tag_add(self, args):
        host = self._isidore.getHost(args[1])
        if len(args) == 4:
            self.subprompt(args, self.host)
            return
        elif args[4] == '?':
            print('''\
?           print this help message
<tag>       name of the tag to add''')
            return

        tag = self._isidore.getTag(args[4])
        if tag == None:
            print("Tag "+args[4]+" does not exist")
            return
        try:
            host.addTag(tag)
        except mysql.connector.Error as e:
            if e.errno == 1062:
                print(host.getHostname()+" already has tag "+args[4], file=sys.stderr)
        except:
            print(traceback.format_exc(),
                    file=sys.stderr)

    # > host <hostname> tag remove
    def host_tag_remove(self, args):
        host = self._isidore.getHost(args[1])
        if len(args) == 4:
            self.subprompt(args, self.host)
            return
        elif args[4] == '?':
            print('''\
?           print this help message
<tag>       name of the tag to remove''')
            return
        tag = self._isidore.getTag(args[4])
        if tag == None:
            print("Tag "+args[4]+" does not exist")
            return
        host.removeTag(tag)

    # > rename
    def rename(self, args):
        if len(args) == 1:
            self.subprompt(args, self.rename)
        elif args[1] == '?':
            print('''\
?           print this help message
host        rename a host
tag         rename a tag''')
        elif args[1] == 'host':
            self.rename_host(args)
        elif args[1] == 'tag':
            self.rename_tag(args)
        else:
            print('Invalid argument '+args[1]+'. Enter ? for help.', file=sys.stderr)

    # > rename host <old_hostname> <new_hostname>
    def rename_host(self, args):
        if len(args) == 2:
            self.subprompt(args, self.rename_host)
            return
        elif args[2] == '?':
            print('''\
?           print this help message
<hostname>  the old hostname''')
            return

        host = self._isidore.getHost(args[2])

        if host == None:
            print("Host "+args[2]+" does not exist.")
            return
        elif len(args) == 3:
            print(\
'''Rename does not allow for a subprompt for the fourth argument. You must
enter both the old and new hostnames at the same time 

Example:
    > rename host foo bar

Enter ? as any argument help.''', file=sys.stderr)
            return
        elif args[3] == '?':
            print('''\
?           print this help message
<hostname>  the new hostname''')
            return

        try:
            host.setHostname(args[3])
        except mysql.connector.Error as e:
            if e.errno == 1062:
                print('Host '+args[3]+' already exists.', file=sys.stderr)
            else:
                print(traceback.format_exc(), file=sys.stderr)
        except:
            print(traceback.format_exc(), file=sys.stderr)

    # > rename tag <old_hostname> <new_hostname>
    def rename_tag(self, args):
        if len(args) == 2:
            self.subprompt(args, self.rename_tag)
            return
        elif args[2] == '?':
            print('''\
?           print this help message
<name>      the old tag name''')
            return

        tag = self._isidore.getTag(args[2])

        if tag == None:
            print("Tag "+args[2]+" does not exist.")
            return
        elif len(args) == 3:
            print(\
'''Rename does not allow for a subprompt for the fourth argument. You must
enter both the old and new tag names at the same time 

Example:
    > rename tag foo bar

Enter ? as any argument help.''', file=sys.stderr)
            return
        elif args[3] == '?':
            print('''\
?           print this help message
<name>      the new tag name''')
            return

        try:
            tag.setName(args[3])
        except mysql.connector.Error as e:
            if e.errno == 1062:
                print('Tag '+args[3]+' already exists.', file=sys.stderr)
            else:
                print(traceback.format_exc(), file=sys.stderr)
        except:
            print(traceback.format_exc(), file=sys.stderr)

    # > tag
    def tag(self, args):
        # Handle arg #1 (tag <ARG1>)
        if len(args) == 1:
            self.subprompt(args, self.tag)
            return
        elif args[1] == '?':
            print('''\
?           print this help message
<tagname>  the name of the tag to edit''')
            return
        tag = self._isidore.getTag(args[1])
        if tag == None:
            print('Tag '+args[1]+' does not exist!')
            return

        # Handle arg #2 (tag foo <ARG2>)
        elif len(args) == 2:
            self.subprompt(args, self.tag)
        elif args[2] == '?':
            print('''\
?           print this help message
describe    print details about tag attributes
host        display and modify hosts that have this tag
set         modify tag attributes
show        display tag attributes
var         display and modify this tag's variables''')
        elif args[2] == 'describe':
            self.tag_describe(args)
        elif args[2] == 'host':
            self.tag_host(args)
        elif args[2] == 'set':
            self.tag_set(args)
        elif args[2] == 'show':
            self.tag_show(args)
        elif args[2] == 'var':
            self.tag_var(args)
        else:
            print('Invalid command '+args[2]+'. Enter ? for help.', file=sys.stderr)

    # > tag <tagname> describe
    def tag_describe(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 3:
            self.subprompt(args, self.tag_describe)
        elif args[3] == '?':
            print('''\
?           print this help message
hosts       describe the hosts currently assigned to this tag''')
        elif args[3] == 'hosts':
            hosts = {}
            for host in tag.getHosts():
                hosts[host.getHostname()] = host.getDescription()
            print(yaml.dump(hosts, default_flow_style=False))
        else:
            print('Invalid argument '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > tag <tagname> host
    def tag_host(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 3:
            self.subprompt(args, self.tag)
        elif args[3] == '?':
            print('''\
?           print this help message
add         assign hosts to this tag
list        display all hosts that have this tag
remove      remove hosts from this tag''')
        elif args[3] == 'add':
            self.tag_host_add(args)
        elif args[3] == 'list':
            for host in tag.getHosts():
                print(host.getHostname())
        elif args[3] == 'remove':
            self.tag_host_remove(args)
        else:
            print('Invalid command '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > tag <tagname> host add
    def tag_host_add(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 4:
            self.subprompt(args, self.tag)
            return
        elif args[4] == '?':
            print('''\
?           print this help message
<host>      name of the host to add''')
            return

        host = self._isidore.getHost(args[4])
        if host == None:
            print("Host "+args[4]+" does not exist")
            return
        try:
            host.addTag(tag)
        except mysql.connector.Error as e:
            if e.errno == 1062:
                print(host.getHostname()+" already has tag "+args[1], file=sys.stderr)
        except:
            print(traceback.format_exc(),
                    file=sys.stderr)

    # > tag <tagname> host remove
    def tag_host_remove(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 4:
            self.subprompt(args, self.tag)
            return
        elif args[4] == '?':
            print('''\
?           print this help message
<host>      name of the host to remove''')
            return
        host = self._isidore.getHost(args[4])
        if host == None:
            print("Host "+args[4]+" does not have tag "+args[1])
            return
        host.removeTag(tag)

    # > tag <tagname> show
    def tag_show(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 3:
            self.subprompt(args, self.tag)
        elif args[3] == '?':
            print('''\
?           print this help message
all         print all the information about the tag
description print the tag's description
group       print the date the tag was commissioned
hosts       print all hosts that have this tag''')
        elif args[3] == 'all':
            print(yaml.dump(tag.getDetails(), default_flow_style=False))
        elif args[3] == 'description':
            print(tag.getDescription())
        elif args[3] == 'group':
            print(tag.getGroup())
        elif args[3] == 'hosts':
            for host in tag.getHosts():
                print(host.getHostname())
        else:
            print('Invalid argument '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > tag <tagname> set
    def tag_set(self, args):
        tag = self._isidore.getTag(args[1])
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
            elif args[4] == 'none':
                tag.setDescription(None)
            else:
                tag.setDescription(args[4])
        else:
            print('Invalid argument '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > tag <tagname> set group
    def tag_set_group(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 4:
            self.subprompt(args, self.tag)
        elif args[4] == '?':
            print('''\
<group>     the tag group
none        remove tag group''')
        elif args[4] == 'none':
            tag.setGroup(None)
        else:
            try:
                tag.setGroup(args[4])
            except:
                print("Failed to set group")

    # > tag <tagname> var
    def tag_var(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 3:
            self.subprompt(args, self.tag_var)
        elif args[3] == '?':
            print('''\
?           print this help message
append      append a value to a list variable
print       print a variable
set         set a variable
unset       unset (delete) a variable''')

        elif args[3] == 'append':
            self.tag_var_append(args)

        elif args[3] == 'print':
            if len(args) == 4:
                print(yaml.dump(
                    tag.getVar(),
                    default_flow_style=False,
                    sort_keys=False))
            elif args[4] == '?':
                print('''\
?           print this help message
$           print all variables
<variable>  name of the variable to print''')
            else:
                print(yaml.dump(
                    tag.getVar(args[4]),
                    default_flow_style=False,
                    sort_keys=False))

        elif args[3] == 'set':
            self.tag_var_set(args)

        elif args[3] == 'unset':
            self.tag_var_unset(args)

        else:
            print('Invalid command '+args[3]+'. Enter ? for help.', file=sys.stderr)

    # > tag <tagname> var append
    def tag_var_append(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 4:
            self.subprompt(args, self.tag_var_append)
        elif args[4] == '?':
            print('''\
?           print this help message
<variable>  name of the list variable to append to''')

        elif len(args) == 5:
            self.subprompt(args, self.tag_var_append)

        elif args[5] == '?':
            print('''\
?           print this help message
<json>      the JSON value to append to the list''')

        else:
            try:
                tag.appendVar(args[4], json.loads(args[5]))
            except json.decoder.JSONDecodeError:
                print(args[5] + '''
^-- this is not valid JSON

Strings must be double quoted. It will be necessary to either nest double
quotes inside single quotes or escape the double quotes like so:

   > tag mytag var set foo '"bar"'

or

   > tag mytag var set foo \\"bar\\"

''')
            except:
                print(\
'Failed to append to list variable. Is %s a valid list path?' % args[4])

    # > tag <tagname> var set
    def tag_var_set(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 4:
            self.subprompt(args, self.tag_var_set)
        elif args[4] == '?':
            print('''\
?           print this help message
$           set/replace the entire variable tree
<variable>  name of the variable to set''')

        elif len(args) == 5:
            self.subprompt(args, self.tag_var_set)

        elif args[5] == '?':
            print('''\
?           print this help message
<json>      the JSON value to set the variable to''')

        else:
            try:
                tag.setVar(args[4], json.loads(args[5]))
            except json.decoder.JSONDecodeError:
                print(args[5] + '''
^-- this is not valid JSON

Strings must be double quoted. It will be necessary to either nest double
quotes inside single quotes or escape the double quotes like so:

   > tag mytag var set foo '"bar"'

or

   > tag mytag var set foo \\"bar\\"

''')

    # > tag <tagname> var unset
    def tag_var_unset(self, args):
        tag = self._isidore.getTag(args[1])
        if len(args) == 4:
            self.subprompt(args, self.tag_var_set)
        elif args[4] == '?':
            print('''\
?           print this help message
<variable>  name of the variable to unset''')
        else:
            try:
                tag.unsetVar(args[4])
            except:
                print("Failed to unset variable %s" % args[4])

    # > version
    def version(self, args):
            print('Isidore Command Prompt version: '+self.getVersion())
            print('libIsidore version: '+self._isidore.getVersion())
            print('Isidore database version: '+self._isidore.getDatabaseVersion())

