# 3. Hosts

1. [Creating Hosts](#1-creating-hosts)
2. [Setting Host Attributes](#2-setting-host-attributes)
   1. [Decommissioning a Host](#1-decommissioning-a-host)
3. [Viewing Host Attributes](#3-viewing-host-attributes)

## 1. Creating Hosts

Hosts are initially added to Isidore using the `create host` command at the
root prompt. To create the host `yoda`:

    > create host yoda

If there are several hosts that need to be created, it's much easier to take
advantage of subprompts:

    > create host
    create host> luke
    create host> leia
    create host> obi-wan
    create host> han
    create host> chewy
    create host> beru
    create host> end
    >

This creates all the remaining hosts from the example in the
[Getting Started section](getting_started.md).

## 2. Setting Host Attributes

Each host has a set of attributes. They are as follows:

* commissioned: The datetime the system was commissioned. Defaults to the
  datetime it was added to Isidore.
* decommissioned: The datetime the system was decommissioned. Defaults to none.
* description: A friendly, human readable description of the system. Defaults
  to none.

Host attributes can be set using the `host <hostname> set <attribute> <value>`
command. For example to set host `han`'s description:

    > host han set description 'Disorganized development laptop. Sorry about this mess.'

### 1. Decommissioning a Host

Isidore considers a host to be decommissioned if it has the decommissioned
attribute set. If its decommissioned attribute is none, then the host is
considered to be commissioned.

To decommission the host beru:

    > host beru set decommissioned now

This sets the decommissioned attribute for beru to the current time.
Alternatively, a specific datetime can be set:

    > host beru set decommissioned 1977-05-25

To recommission a host, clear its decommissioned attribute:

    > host beru set decommissioned none

Note that decommissioned hosts will not show up when listing hosts or
generating the Ansible inventory.

## 3. Viewing Host Attributes

To view an attribute, use the `host <hostname> show <attribute>` command. For
example, to view host `han`'s description:

    > host han show description
    Disorganized development laptop. Sorry about this mess.
    >

To display all the attributes in a friendly YAML format, use `host <hostname> show all`:

    > host han show all
    han:
      commissioned: '2023-05-04 10:46:50'
      decommissioned: 'None'
      description: 'Disorganized development laptop. Sorry about this mess.'
      tags:

