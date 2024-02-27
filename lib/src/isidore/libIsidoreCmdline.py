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
import readline

from isidore.libIsidore import *

# The Isidore command prompt
class IsidoreCmdline:

    _isidore = None
    _version = '0.1.6'

    # Creates a new Isidore command prompt
    # @param isidore    The underlying Isidore instance for the command prompt
    #                   to connect to.
    def __init__(self, isidore):
        self._isidore = isidore
        self.navigation = {
            'config': {
                'description': 'Configure the Isidore installation',
                'args': 'config',
                'method': self.config,
                'subcommands': {
                    'show': {
                        'description': 'Print various data about the Isidore installation',
                        'function': self.config_show,
                    },
                    'set': {
                        'description': 'Modify the Isidore installation',
                        'function': self.config_set,
                    }
                }
            },
            'show': {
                'description': 'Show various information',
                'args': 'show',
                'method': self.show,
                'subcommands': {
                    'config': {
                        'description': 'Print the commands to populate the database with the current configuration',
                        'function': self.show_config,
                    },
                    'hosts': {
                        'description': 'Print all commissioned hosts in the database',
                        'function': self.show_hosts,
                    },
                    'inventory': {
                        'description': 'Print the full Ansible inventory file',
                        'function': self.show_inventory,
                        'subcommands': {  #subcommands for show inventory
                            'human': {
                                'description': 'Print the inventory in a human-friendly format',
                            },
                            'ini': {
                                'description': 'Print the inventory in INI format',
                            },
                            'json': {
                                'description': 'Print the inventory in JSON format',
                            },
                            'yaml': {
                                'description': 'Print the inventory in YAML format',
                            }
                        }
                    },
                    'graveyard': {
                        'description': 'Print all decommissioned hosts in the database',
                        'function': self.show_graveyard,
                    },
                    'tag-groups': {
                        'description': 'Print all the tag groups in the database',
                        'function': self.show_taggroups,
                    },
                    'tags': {
                        'description': 'Print all tags in the database',
                        'function': self.show_tags,
                    }
                }
            },
            'describe': {
                'description': 'Describe various entities',
                'args': 'describe',
                'method': self.describe,
                'subcommands': {
                    'hosts': {
                        'description': 'Describe all commissioned hosts in the database',
                        'function': self.describe_hosts,
                    },
                    'graveyard': {
                        'description': 'Describe all decommissioned hosts in the database',
                        'function': self.describe_graveyard,
                    },
                    'tag-groups': {
                        'description': 'Describe all the tag groups in the database',
                        'function': self.describe_taggroups,
                    },
                    'tags': {
                        'description': 'Describe all tags in the database',
                        'function': self.describe_tags,
                    }
                }
            },
            'echo': {
                'description': 'Echo command',
                'args': 'echo',
                'method': self.echo
            },
            'help': {
                'description': 'Help menu',
                'args': 'help',
                'method': self.help
            },
            'create': {
                'description': 'Create new entities',
                'args': 'create',
                'method': self.create,
                'subcommands': {
                    'host': {
                        'description': 'Create a new host',
                        'function': self.create_host,
                    },
                    'tag': {
                        'description': 'Create a new tag',
                        'function': self.create_tag,
                    }
                }
            },
            'delete': {
                'description': 'Delete entities',
                'args': 'delete',
                'method': self.delete,
                'subcommands': {
                    'host': {
                        'description': 'Delete a host',
                        'function': self.delete_host,
                    },
                    'tag': {
                        'description': 'Delete a tag',
                        'function': self.delete_tag,
                    }
                }
            },
            'host': {
                'description': 'Operations on a specific host',
                'args': 'host',
                'method': self.host,
                'subcommands': {
                    'describe': {
                        'description': 'Print details about host attributes',
                        'function': self.host_describe,
                    },
                    'set': {
                        'description': 'Modify host attributes',
                        'function': self.host_set,
                    },
                    'show': {
                        'description': 'Display host attributes',
                        'function': self.host_show,
                    },
                    'tag': {
                        'description': 'Display and modify this host\'s tags',
                        'function': self.host_tag,
                    },
                    'var': {
                        'description': 'Display and modify this host\'s variables',
                        'function': self.host_var,
                    }
                }
            },
            'tag': {
                'description': 'Operations on a specific tag',
                'args': 'tag',
                'method': self.tag,
                'subcommands': {
                    'describe': {
                        'description': 'Print details about tag attributes',
                        'function': self.tag_describe,
                    },
                    'host': {
                        'description': 'Display and modify hosts that have this tag',
                        'function': self.tag_host,
                    },
                    'set': {
                        'description': 'Modify tag attributes',
                        'function': self.tag_set,
                    },
                    'show': {
                        'description': 'Display tag attributes',
                        'function': self.tag_show,
                        'subcommands': {
                            'all': {
                                'description': 'Print all the information about the tag',
                            },
                            'description': {
                                'description': 'Print the tag\'s description',
                            },
                            'group': {
                                'description': 'Print the date the tag was commissioned',
                            },
                            'hosts': {
                                'description': 'Print all hosts that have this tag',
                            },
                        }
                    },
                    'var': {
                        'description': 'Display and modify this tag\'s variables',
                        'function': self.tag_var,
                    }
                }
            },
            'version': {
                'description': 'Display version information',
                'args': 'version',
                'method': self.version,
                # No subcommands are necessary for the version command
            },
            # Other commands can be structured similarly
        }


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
            name = self._isidore.getName()
            if sys.stdin.isatty():
                display_prompt = ' '.join( \
                    ['[' + name + ']'] + prompt if name else prompt ) + '> '
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

            # Ensure each command runs as its own SQL transaction so each
            # separate command operates on the latest data but still has
            # repeatable reads/consistency within each command.
            self._isidore.newTransaction()

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
        self.setup_tab_completion()
        if sys.stdin.isatty():
            motd = self._isidore.getMotd()
            if motd != None:
                print(motd)
        self.subprompt([], self.rootprompt)

    def _complete_command(self, text, state):
        buffer = readline.get_line_buffer()
        line_parts = shlex.split(buffer)[:state + 1] if buffer else []

        options = []
        current_level = self.navigation

        for part in line_parts[:-1]:  # Traverse through entered parts except the last one
            if part in current_level and 'subcommands' in current_level[part]:
                current_level = current_level[part]['subcommands']
            elif 'subcommands' in current_level and part in current_level['subcommands']:
                current_level = current_level['subcommands'][part]
            else:
                options = []  # Reset options if no subcommands match
                break

        # Suggest commands or subcommands based on the current level and text
        if 'subcommands' in current_level:
            options = [cmd + ' ' for cmd in current_level.keys() if cmd.startswith(text)]
        elif len(line_parts) == 1:
            options = [cmd + ' ' for cmd in self.navigation.keys() if cmd.startswith(text)]

        try:
            return options[state]
        except IndexError:
            return None

    def setup_tab_completion(self):
        readline.set_completer(self._complete_command)
        readline.parse_and_bind("tab: complete")

    # >
    def rootprompt(self, args):
        if args and args[0] in self.navigation:
            command_info = self.navigation[args[0]]
            if 'method' in command_info:
                command_info['method'](args)
            else:
                print(f'Invalid command {args[0]}. Enter ? for help.', file=sys.stderr)
        elif args[0] == '?':
            self.help(args)
        else:
            print(f'Invalid command {args[0]}. Enter ? for help.', file=sys.stderr)

    # > ?
    def help(self, args):
        help_text = [
            ('?', 'print this help message'),
            ('config', 'configure the Isidore installation'),
            ('create', 'create various objects (such as hosts and tags)'),
            ('delete', 'delete various objects (such as hosts and tags)'),
            ('describe', 'print details about various data'),
            ('echo', 'print text back to the console'),
            ('help', 'alias for ?'),
            ('host', 'manipulate a host'),
            ('rename', 'rename various objects (such as hosts and tags)'),
            ('show', 'print various data'),
            ('tag', 'manipulate a tag'),
            ('version', 'display Isidore version information'),
        ]

        max_cmd_length = max(len(cmd) for cmd, _ in help_text)
        for cmd, description in help_text:
            print(f"{cmd.ljust(max_cmd_length + 4)}{description}")

    # > show
    def show(self, args):
        if len(args) == 1:
            self.subprompt(args, self.show)
        elif args[1] in self.navigation['show']['subcommands']:
            self.navigation['show']['subcommands'][args[1]]['function'](args)
        elif args[1] == '?':
            for cmd, details in self.navigation['show']['subcommands'].items():
                print(f"{cmd}        {details['description']}")
        else:
            print(f'Invalid argument {args[1]}. Enter ? for help.', file=sys.stderr)

    # > show config
    def show_config(self, args):
        hosts = self._isidore.getHosts()
        tags = self._isidore.getTags()

        # Isidore Configuration

        ## Header
        print("echo 'Setting global configuration'")

        ## Message of the Day
        motd = self._isidore.getMotd()
        if motd:
            print("config set motd '"+motd.replace("'", "'\"'\"'")+"'")

        ## Name
        name = self._isidore.getName()
        if name:
            print("config set name '"+name.replace("'", "'\"'\"'")+"'")

        ## Blank line for sepeartion
        print()

        # Create Hosts
        print("echo 'Creating hosts'")
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
        print("echo 'Creating tags'")
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
        print("echo 'Assigning tags to hosts'")
        for host in hosts:
            hostname = "'"+host.getHostname().replace("'", "'\"'\"'")+"'"
            for tag in host.getTags():
                print("host "+hostname+" tag add '"+\
                        str(tag.getName()).replace("'", "'\"'\"'")+"'")
        print()

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

        elif len(args) > 2:
            if args[2] == '?':
                for format, details in self.navigation['show']['subcommands']['inventory']['subcommands'].items():
                    print(f"{format}        {details['description']}")
            elif args[2] in self.navigation['show']['subcommands']['inventory']['subcommands']:
                inventory_method = f"getInventory{args[2].capitalize()}"
                if hasattr(self._isidore, inventory_method):
                    print(getattr(self._isidore, inventory_method)())
                else:
                    print(f"Invalid format {args[2]}. Enter ? for help.", file=sys.stderr)
            else:
                print(f'Invalid format {args[2]}. Enter ? for help.', file=sys.stderr)

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
        elif args[1] in self.navigation['describe']['subcommands']:
            self.navigation['describe']['subcommands'][args[1]]['function'](args)
        elif args[1] == '?':
            for cmd, details in self.navigation['describe']['subcommands'].items():
                print(f"{cmd}        {details['description']}")
        else:
            print(f'Invalid argument {args[1]}. Enter ? for help.', file=sys.stderr)

    # > decribe hosts
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

    # > config
    def config(self, args):
        if len(args) == 1:
            self.subprompt(['config'], self.config)
        elif args[1] in self.navigation['config']['subcommands']:
            self.navigation['config']['subcommands'][args[1]]['function'](args)
        elif args[1] == '?':
            for cmd, details in self.navigation['config']['subcommands'].items():
                print(f"{cmd}        {details['description']}")
        else:
            print(f'Invalid argument {args[1]}. Enter ? for help.', file=sys.stderr)

    # > config set
    def config_set(self, args):
        if len(args) == 2:
            self.subprompt(args, self.config_set)
        elif args[2] == '?':
            print('''\
?           print this help message
motd        set the message of the day
name        set the name of the isidore instance''')
        elif args[2] == 'motd':
            if len(args) == 3:
                print('''\
<motd>          the message of the day
none            clear the message of the day''')
            elif args[3] == 'none':
                self._isidore.setMotd(None)
            else:
                self._isidore.setMotd(args[3])
        elif args[2] == 'name':
            if len(args) == 3:
                print('''\
<name>          the instance name
none            clear the instance name''')
            elif args[3] == 'none':
                self._isidore.setName(None)
            else:
                self._isidore.setName(args[3])
        else:
            print('Invalid argument '+args[2]+'. Enter ? for help.', file=sys.stderr)

    # > config show
    def config_show(self, args):
        if len(args) == 2:
            self.subprompt(args, self.config_show)
        elif args[2] == '?':
            print('''\
?           print this help message
connection  display information about SQL database connection
motd        display the message of the day
name        display the name of the Isidore instance
version     display Isidore version information''')
        elif args[2] == 'connection':
            print(yaml.dump({
                'user': self._isidore.getDatabaseUser(),
                'host': self._isidore.getDatabaseHost(),
                'database': self._isidore.getDatabaseName()
            }, default_flow_style=False))
        elif args[2] == 'motd':
            print(self._isidore.getMotd())
        elif args[2] == 'name':
            print(self._isidore.getName())
        elif args[2] == 'version':
            self.version(None)
        else:
            print('Invalid argument '+args[2]+'. Enter ? for help.', file=sys.stderr)

    # > create
    def create(self, args):
        if len(args) == 1:
            self.subprompt(['create'], self.create)
        elif args[1] in self.navigation['create']['subcommands']:
            self.navigation['create']['subcommands'][args[1]]['function'](args)
        elif args[1] == '?':
            for cmd, details in self.navigation['create']['subcommands'].items():
                print(f"{cmd}        {details['description']}")
        else:
            print(f'Invalid argument {args[1]}. Enter ? for help.', file=sys.stderr)


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
            self.subprompt(['delete'], self.delete)
        elif args[1] in self.navigation['delete']['subcommands']:
            self.navigation['delete']['subcommands'][args[1]]['function'](args)
        elif args[1] == '?':
            for cmd, details in self.navigation['delete']['subcommands'].items():
                print(f"{cmd}        {details['description']}")
        else:
            print(f'Invalid argument {args[1]}. Enter ? for help.', file=sys.stderr)


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
        # Initial handling for just 'host' or 'host ?'
        if len(args) == 1 or (len(args) == 2 and args[1] == '?'):
            print('''\
?           print this help message
<hostname>  the name of the host to edit''')
            # Optional: List available hosts for selection or guidance
            # self.list_hosts()
            return

        # Check if the hostname provided exists in the Isidore database
        host = self._isidore.getHost(args[1])
        if host is None:
            print(f'Host {args[1]} does not exist!')
            return

        # If only the hostname is provided, enter into subprompt for this specific host
        if len(args) == 2:
            self.subprompt(args, self.host)

        # Handle second-level subcommands for the host
        elif len(args) > 2:
            if args[2] in self.navigation['host']['subcommands']:
                self.navigation['host']['subcommands'][args[2]]['function'](args)
            elif args[2] == '?':
                for cmd, details in self.navigation['host']['subcommands'].items():
                    print(f"{cmd}        {details['description']}")
            else:
                print(f'Invalid command {args[2]}. Enter ? for help.', file=sys.stderr)

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
        # Initial handling for just 'tag' or 'tag ?'
        if len(args) == 1 or (len(args) == 2 and args[1] == '?'):
            print('''\
?           print this help message
<tagname>   the name of the tag to edit''')
            return

        # Fetch the specified tag to see if it exists
        tag = self._isidore.getTag(args[1])
        if tag is None:
            print(f'Tag {args[1]} does not exist!')
            return

        if len(args) == 2:
            self.subprompt(args, self.tag)
            return

        if len(args) > 2:
            if args[2] in self.navigation['tag']['subcommands']:
                self.navigation['tag']['subcommands'][args[2]]['function'](args)
            elif args[2] == '?':
                for cmd, details in self.navigation['tag']['subcommands'].items():
                    print(f"{cmd}        {details['description']}")
            else:
                print(f'Invalid command {args[2]}. Enter ? for help.', file=sys.stderr)

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
            self.subprompt(args, self.tag_show)
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
            hosts = tag.getHosts()
            for host in hosts:
                print(host.getHostname())
        else:
            print('Invalid argument ' + args[3] + '. Enter ? for help.', file=sys.stderr)

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
