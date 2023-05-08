# 2. Getting Started

1. [Overview of Isidore's Design](#1-overview-of-isidores-design)
2. [Isidore Command Prompt Basics](#2-isidore-command-prompt-basics)

## 1. Overview of Isidore's Design

### Ths Issue with Ansible Inventory Management

One of the great strengths of Ansible is the ability to subdivide its inventory
into host groups. Very often, hosts need to belong to more than one group. Take
the following example with these systems:

| Hostname | Location        | Physicality | Type        |
| -------- | --------------- | ----------- | ----------- |
| yoda     | Newark, NJ      | physical    | server      |
| luke     | Newark, NJ      | virtual     | server      | 
| leia     | Princeton, NJ   | physical    | workstation |
| obi-wan  | Princeton, NJ   | physical    | server      |
| han      | Cherry Hill, NJ | physical    | laptop      |
| chewy    | Cherry Hill, NJ | physical    | server      |
| beru     | Cherry Hill, NJ | virtual     | workstation |

There are three locations, two options for physicality, and three options for
type. Depending on the playbook, it may be necessary to select based off of any
combination of these.

The Ansible project's recommended method is to create a series of groups for
location, physicality, and type. For example, the host `yoda` might belong to
the following groups:

* newark
* physical
* server

Meanwhile the host `beru` might belong to the following:

* cherryhill
* virtual
* workstation

There are a few ways this can be implemented that will be explored below:

### Possible Solutions

1. Require all systems to reside in Newark, New Jersey (bad).
2. Require all systems to reside in Princeton, New Jersey (bad but not as bad)
3. Use a series of subgroups (not as bad as the first two but still not great
   either).
4. Use a tag based approach and set operations to select hosts (better).

#### 1. Require all systems to reside in Newark, New Jersey

This approach is neither feasible nor safe. What if you need to do maintenance
at 2 AM?

#### 2. Require all systems to reside in Princeton, New Jersey

This is much safer but still not feasible.

#### 3. Use a series of subgroups

Now for the first approach that's actually somewhat feasible.

From an implementation perspective, the top level of our invetory might be
broken down into the following three groups:

* server
* workstation
* laptop

Each group might then have three child groups for each location:

* newark
* princeton
* cherryhill

Finally, a third level of groups is needed for the physicality:

* physical
* virtual

As such, the full heirarchy of the groups is as follows with each increase in
indentation representing another level of subgroups:

* server
  * newark_server
    * physical_newark_server
    * virtual_newark_server
  * princeton
    * physical_princeton_server
    * virtual_princeton_server
  * cherry_hill
    * physical_cherryhill_server
    * virtual_cherryhill_server
* workstation
  * newark_workstation
    * physical_newark_workstation
    * virtual_newark_workstation
  * princeton_workstation
    * physical_princeton_workstation
    * virtual_princeton_workstation
  * cherryhill_workstation
    * physical_cherryhill_workstation
    * virtual_cherryhill_workstation
* laptop
  * newark_laptop
    * physical_newark_laptop
    * virtual_newark_server
  * princeton_laptop
    * physical_princeton_laptop
    * virtual_princeton_laptop
  * cherryhill_laptop
    * physical_cherryhill_laptop
    * virtual_cherryhill_laptop

So `yoda` would reside in the `physical_newark_server` group and `beru` would
reside in the `virtual_cherryhill_workstation` group.

To target all the systems in Newark, one would use `newark` as the value for
the host field in his Ansible playbook. To target only the servers in Newark,
one would use `newark_servers`.

This results in a total of 18 (3 x 3 x 2) different groups getting created.
This approach works fine in small environments, but as the levels of heirarchy
and the number of options for each level increase, the number of groups grows
exponentially. This approach quickly becomes unmanageable in large, complex
environments.

#### 4. Use a tag based approach

Ansible allows a single host to belong to multiple groups. An alternate
approach that utilizes this is to create every group as a top level group and
have one group for each option. Using this approach, the inventory from the
previous section would be broken down into the following groups:

* newark
* princeton
* cherryhill
* physical
* virtual
* server
* workstaiton
* laptop

Going back to the example hosts, `yoda` would now blong to the following three
groups:

* newark
* physical
* server

##### 4b. Set operations to select hosts

A powerful feature of Ansible is that it allows for the use of set operations
when selecting hosts. This allows for all the servers in Newark to be selected
using `newark:&server`. To select all the virtual workstations in Cherry Hill,
use `cherryhill:&workstation:&virtual`.

##### 4c. It's better but there's still an issue

This approach scales much better in large, complex environments. Since there is
only one group created for each new option that's added, the number of groups
grows linearly instead of exponentially.

The problem is that systems must now be added to the inventory file several
times: once for each group. While this is just an inconvenience when adding a
single system, it gets to be quite cumbersome when you need to add several
systems. Additionally decommissioning systems becomes error prone as care must
be taken to ensure that every occurrance of it is removed.

### Where Isidore Comes In

This is where Isidore comes in. It allows for approach four to be taken, but
instead of using flat files it stores your hosts in a MySQL database. Each host
can then be assigned to one or more tags.

For the example hosts in the previous section, the following tags would be
present in Isidore. These correspond to the groups created in approach four.

* newark
* princeton
* cherryhill
* physical
* virtual
* server
* workstaiton
* laptop

The hosts would have the following tags:

* yoda
  * newark
  * physical
  * server
* luke
  * newark
  * virtual
  * server
* leia
  * princeton
  * physical
  * workstation
* obi-wan
  * princeton
  * physical
  * workstation
* han
  * cherryhill
  * physical
  * laptop
* chewy
  * cherryhill
  * physical
  * server
* beru
  * cherryhill
  * virtual
  * server

## 2. Isidore Command Prompt Basics

### 1. Starting the Command Prompt

The Isidore command prompt is started by running the `isidore` command. Once
started, you will find yourself at the root prompt, delineated by `> `.

    > 

### 2. Entering Commands

The command prompt supports standard, shell like syntax for entering commands
like so:

    > command arg1 arg2 arg3

Quoting or escaping can be used for multi word arguments:

    > command "Argument 1" 'Argument 2' Argument\ 3

The command prompt uses GNU Readline, so command history and reverse searching
work the same way they do in a Bash shell.

Additionally, Vi like editing is supported. Press `escape` to activate it and
`i` to go back into insert mode.

### 3. Getting Help

At any point, you can view a summary of all the available commands or arguments
by entering a single `?` character.

For help at the root prompt:

    > ?
    ^C          clear the current command
    ^D          alias for end
    end         go back to the previous prompt
    quit        exit
    ?           print this help message
    create      create various objects (such as hosts and tags)
    echo        print text back to the console
    help        alias for ?
    host        manipulate a host
    show        print various data
    tag         manipulate a tag
    version     display Isidore version information

To see what the valid arguments are to the show command.

    > show ?
    ^C          clear the current command
    ^D          alias for end
    end         go back to the previous prompt
    quit        exit
    ?           print this help message
    config      print the commmands to populate the database with the current
                configuration
    hosts       print all commissioned hosts in the database
    graveyard   print all decommissioned hosts in the database
    inventory   print the full Ansible inventory file
    tag-groups  print all the tag groups in the database
    tags        print all tags in the database

### 4. Subprompts

To save users from having to enter the same prefix to a command over and over,
Isidore supports entering into subprompt levels. This is very similar to the
subprompt feature of the Cisco IOS.

When an incomplete command is entered, Isidore drops you to a subprompt. For
example, entering the following command will drop you to the `show` level
subprompt:

    > show
    show>

Now every command you run will have `show` prefixed to it as the first
argument. Entering `?` now is akin to entering `show ?` at the root prompt:

    show> ?
    ^C          clear the current command
    ^D          alias for end
    end         go back to the previous prompt
    quit        exit
    ?           print this help message
    config      print the commmands to populate the database with the current
                configuration
    hosts       print all commissioned hosts in the database
    graveyard   print all decommissioned hosts in the database
    inventory   print the full Ansible inventory file
    tag-groups  print all the tag groups in the database
    tags        print all tags in the database
    show>

When in a subprompt, the current subprompt string will be displayed before the
`>` symbol. To exit the subprompt and go back to the previous prompt, enter the
`end` command:

    show> end
    >

### 5. Super Commands

Generally the commands that are available differ depending on your subprompt;
however, there are a few super commands that work the same at every subprompt.
They are as follows:

#### end

Returns you to your previous prompt.

#### quit

Immediately quits the Isidore command prompt.

#### ^C (control + C)

Clears the command you are currently typing and gives you a fresh prompt to
start over. This is akin to how ^C works in Bash/Csh.

#### ^D (control + D)

Does the same thing as `end`.

#### ?

Lists the valid commands at the current prompt.

