# 2. Getting Started

1. [Overview of Isidore's Design](#1. Overview of Isidore's Design)
2. [Isidore Command Prompt Basics](#2. Isidore Command Prompt Basics)

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

