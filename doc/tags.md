# 4. Tags

1. [Creating Tags](#1-creating-tags)
2. [Setting Tag Attributes](#2-setting-tag-attributes)
3. [Viewing Tag Attributes](#3-viewing-tag-attributes)
4. [Tag Groups](#4-tag-groups)
5. [Renaming Tags](#5-renaming-tags)
6. [Deleting Tags](#6-deleting-tags)

## 1. Creating Tags

Tags are initially added to Isidore using the `create tag` command at the
root prompt. To create the tag `newark`:

    > create tag newark

Just as when creating tags, a subprompt can be used to quickly add several
tags:

    > create tag
    create tag> princeton
    create tag> cherryhill
    create tag> physical
    create tag> virtual
    create tag> server
    create tag> workstaion
    create tag> laptop
    >

This creates all the remaining tags from the example in the
[Getting Started section](getting_started.md).

## 2. Setting Tag Attributes

Like hosts, each tag has a set of attributes. They are as follows:

* group: The group that the tag belongs to
* description: A friendly, human readable description of the system. Defaults
  to none.

Tag attributes can be set using the `tag <tagname> set <attribute> <value>`
command. For example to set tag `newark`'s description:

    > tag newark set description 'Newark, NJ'

## 3. Viewing Tag Attributes

To view an attribute, use the `tag <tagname> show <attribute>` command. For
example, to view tag `newark`'s description:

    > tag newark show description
    Newark, NJ
    >

To display all the attributes in a friendly YAML format, use `tag <tagname> show all`:

    > tag newark show all
    newark:
      hosts: []
      vars:
        isidore:
          group: 'location'
          description: 'Newark, NJ'
    >

## 4. Tag Groups

Very often, it makes sense to organize tags into groups depending on what they
describe about the system. For instance, in the example the tags `newark`,
`princeton`, and `cherryhill` all describe locations while `server`,
`workstation`, and `laptop` describe the system type.

Each tag can be assigned a group using the `tag <tagname> set group <group>`
command. For example:

    > tag newark set group location

To set the groups for the other tags from the example:

    > tag princeton set group location
    > tag cherryhill set group location
    > tag server set group type
    > tag workstation set group type
    > tag laptop set group type
    > tag physical set group physicality
    > tag virtual set group physicality

To display all the tags organized by group, use the `show tag-groups` command:

    > show tag-groups
    location (cherryhill, newark, princeton)
    physicality (physical, virtual)
    type (laptop, server, workstation)
    >

## 5. Renaming Tags

Tags can be renamed using the `rename tag` command at the root prompt. To
rename the tag `workstation` to `desktop`:

    > rename tag workstation desktop

## 6. Deleting Tags

Before a tag can be deleted, it must not have any hosts assigned to it. Once
all the hosts have been removed, the tag can be deleted using the `delete tag`
command at the root prompt. To delete the host `camden`:

    > delete tag camden

