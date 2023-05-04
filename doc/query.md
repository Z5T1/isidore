# 6. Querying Data

1. [Listing Hosts](#listing-hosts)
2. [Listing Tags](#listing-tags)
3. [Printing the Inventory](#printing-the-inventory)
4. [Printing the Isidore Configuration](#printing-the-isidore-configuration)

## 1. Listing Hosts

To list all the commissioned hosts in the Isidore database, use the
`show hosts` command.

    > show hosts
    chewy
    han
    leia
    luke
    obi-wan
    yoda
    >

To list all the decommissioned hosts in the Isidore database, use the
`show graveyard` command.

    > show graveyard
    beru
    >

## 2. Listing Tags

To list all the tags in the Isidore database, use the `show tags` command.

    > show tags
    cherryhill
    laptop
    newark
    physical
    princeton
    server
    virtual
    workstation
    >

To list all the tags in the Isidore database organized by group, use the
`show tag-groups` command.

    > show tag-groups
    location (cherryhill, newark, princeton)
    physicality (physical, virtual)
    type (laptop, server, workstation)
    >

## 3. Printing the Inventory

To print the full inventory suitable for use with Ansible, use the `show
inventory` command:

    > show inventory
    # All Host
    beru
    chewy
    han
    leia
    luke
    obi-wan
    yoda
    
    # location: cherryhill (None)
    [cherryhill]
    chewy
    han
    
    # location: newark (Newark, NJ)
    [newark]
    luke
    yoda
    
    # location: princeton (None)
    [princeton]
    leia
    obi-wan
    
    # physicality: physical (None)
    [physical]
    chewy
    han
    leia
    obi-wan
    yoda
    
    # physicality: virtual (None)
    [virtual]
    luke
    
    # type: laptop (None)
    [laptop]
    han
    
    # type: server (None)
    [server]
    chewy
    luke
    yoda
    
    # type: workstation (None)
    [workstation]
    leia
    obi-wan
    
    
    >

There is also an `inventory` Python script provided with the Isidore
installation. It resides in your Isidore binary directory (by default
/opt/isidore/bin). To print the inventory this way, run:

    solo@han:~$ /opt/isidore/bin/inventory

This script is also suitable for use as an Ansible inventory source. For
example, the following can be used to run the site.yml playbook on the Isidore
inventory:

    solo@han:ansible$ ansible-playbook site.yml -i /opt/isidore/bin/inventory

## 4. Printing the Isidore Configuration

For backup and portability purposes, it is possible to print all of the Isidore
commands that are necessary to recreate your database on a clean, empty
installation. This can be done by running the `show config` command.

