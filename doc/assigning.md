# 5. Assigning Tags to Hosts

1. [Assigning Tags to a Host](#1-assigning-tags-to-a-host)
2. [Listing Tags Assigned to a Host](#2-listing-tags-assigned-to-a-host)
3. [Assigning Hosts to a Tag](#3-assigning-hosts-to-a-tag)
4. [Listing Hosts Assigned to a Tag](#4-listing-hosts-assigned-to-a-tag)

## 1. Assigning Tags to a Host

To assign a tag to a host, use the `host <hostname> tag add <tagname>` command.
For example, to assign the `newark` tag to the host `yoda` use the following
command:

    > host yoda tag add newark

To unassign a tag, replace `add` with `remove`:

    > host yoda tag remove newark

Using a subprompt makes it easy to quickly add several tags to a host:

    > host yoda tag add
    host yoda tag add> newark
    host yoda tag add> physical
    host yoda tag add> server
    host yoda tag add> end
    >

## 2. Listing Tags Assigned to a Host

To list the tags that are assigned to a host, use the `host <hostname> tag
list` command. For example, to view host `yoda`'s tags:

    > host yoda tag list
    newark
    physical
    server
    >

Additionally, all of a hosts tags along with their corresponding groups is
displayed as part of `host <hostname> show all`:

    > host yoda show all
    yoda:
      commissioned: '2023-05-04 10:46:50'
      decommissioned: 'None'
      description: 'None'
      tags:
        - 'location': 'newark'
        - 'physicality': 'physical'
        - 'type': 'server'
    
    >

## 3. Assigning Hosts to a Tag

As a convenience mechanism, it is also possible to assign a host to a tag using
the `tag <tagname> host add <hostname>`. To assign the host `luke` to the
`newark` tag, use the following:

    > tag newark host add luke

This accomplishes the same thing as

    > host like tag add newark

Similarly, one can remove a host from a tag this way:

    > tag newark host remove luke

This can be used in conjunction with subprompts to quickly add several hosts to
a tag. To assign all the hosts to the `cherryhill` tag from the example, the
following can be used:

    > tag cherryhill host add
    tag cherryhill host add> han
    tag cherryhill host add> chewy
    tag cherryhill host add> beru
    tag cherryhill host add> end
    > 

## 4. Listing Hosts Assigned to a Tag

The hosts assigned to a tag can also be listed using the following command:
`tag <tagname> host list`. For example, to list all systems that have the
server tag:

    > tag server host list
    beru
    chewy
    luke
    yoda
    >

