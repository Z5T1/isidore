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

import mysql.connector
import yaml
import json

class Isidore:

    _conn = None
    _version = '0.1.0'

    def __init__(self, user, password, host, database):
        self._conn = mysql.connector.connect(
                user = user,
                password = password,
                host = host,
                database = database
        )

    # Creates a new host in the database
    # @param hostname           The hostname for the new host
    def createHost(self, hostname):
        cursor = self._conn.cursor()
        stmt = "INSERT INTO Host (Hostname) VALUES (%s)"
        cursor.execute(stmt, [ hostname ])
        self._conn.commit()
        cursor.close()

    # Creates a new tag in the database
    # @param name               The name for the new tag
    def createTag(self, name):
        cursor = self._conn.cursor()
        stmt = "INSERT INTO Tag (TagName) VALUES (%s)"
        cursor.execute(stmt, [ name ])
        self._conn.commit()
        cursor.close()

    # Gets all the commissioned hosts in the database
    # @return   An array containing all the commissioned hosts in
    #           the database
    def getCommissionedHosts(self):
        hosts = list()

        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM Host WHERE DecommissionDate IS NULL ORDER BY Hostname ASC")
        for (hostId, hostname, commissionDate, decommissionDate, description) in cursor:
            host = Host(hostId, hostname, commissionDate,
                    decommissionDate, description, self)
            hosts.append(host)
        cursor.close()

        return hosts

    # Gets all the decommissioned hosts in the database
    # @return   An array containing all the decommissioned hosts in
    #           the database
    def getDecommissionedHosts(self):
        hosts = list()

        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM Host WHERE DecommissionDate IS NOT NULL ORDER BY Hostname ASC")
        for (hostId, hostname, commissionDate, decommissionDate, description) in cursor:
            host = Host(hostId, hostname, commissionDate,
                    decommissionDate, description, self)
            hosts.append(host)
        cursor.close()

        return hosts

    # Gets a host in the database
    # @param hostname   The hostname of the system to get
    # @return           The Host object, or None if the host does
    #                   not exist.
    def getHost(self, hostname):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM Host WHERE Hostname = %s",
                [hostname])

        row = cursor.fetchone()
        if row == None:
            return None

        host = Host(row[0], row[1], row[2], row[3], row[4],
                self)
        cursor.fetchall()
        cursor.close()
        return host

    # Gets all the hosts in the database
    # @return   An array containing all the hosts in the database
    def getHosts(self):
        hosts = list()

        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM Host ORDER BY Hostname ASC")
        for (hostId, hostname, commissionDate, decommissionDate, description) in cursor:
            host = Host(hostId, hostname, commissionDate,
                    decommissionDate, description, self)
            hosts.append(host)
        cursor.close()

        return hosts

    # Builds an Ansible inventory in a dictionary representation
    # from all hosts and tags in the database
    # @return       the Ansible inventory dictionary
    #               representation 
    def getInventory(self):
        inv = dict()

        # Add all the hosts without a group header to ensure every
        # system is included, even those without any tags.
        inv['all'] = {
                'hosts': list()
        }
        for host in self.getCommissionedHosts():
            inv['all']['hosts'].append(host.getDetails())

        # Add each tag and its hosts as a group
        for tag in self.getTags(True):
            name = tag.getName()
            inv[name] = tag.getDetails()[name]

        return inv

    # Builds an Ansible INI inventory from all hosts and tags in
    # the database
    # @return       the Ansible inventory INI representation as a
    #               string
    def getInventoryIni(self):
        inv = ""

        # Add all the hosts without a group header to ensure every
        # system is included, even those without any tags.
        inv += "# All Host\n"
        for host in self.getCommissionedHosts():
            inv += host.getHostname() + "\n"
        inv += "\n"

        # Print each tag and its hosts as a group
        for tag in self.getTags(True):
            # Comment
            group = tag.getGroup()
            if group == None:
                inv += "# "+tag.getName()+\
                        " ("+str(tag.getDescription())+")\n"
            else:
                inv += "# "+tag.getGroup()+": "+tag.getName()+\
                        " ("+str(tag.getDescription())+")\n"

            # Header
            inv += "["+tag.getName()+"]\n"

            # Hosts
            for host in tag.getHosts():
                inv += host.getHostname() + "\n"
            inv += "\n"

        return inv

    # Builds an Ansible inventory in JSON format from all hosts
    # and tags in the database
    # @return       the Ansible JSON inventory as a string
    def getInventoryJson(self):
        inv = dict()

        # Add meta section
        inv['_meta'] = {
                'hostvars': {}
        }

        # Add all the hosts without a group header to ensure every
        # system is included, even those without any tags.
        inv['all'] = {
                'hosts': list()
        }
        for host in self.getCommissionedHosts():
            name = host.getHostname()
            inv['all']['hosts'].append(name)
            inv['_meta']['hostvars'][name] = host.getDetails()[name]['vars']

        # Add each tag and its hosts as a group
        for tag in self.getTags(True):
            name = tag.getName()
            inv[name] = tag.getDetails()[name]

        return json.dumps(inv)

    # Builds an Ansible inventory in YAML format from all hosts
    # and tags in the database
    # @return       the Ansible YAML inventory as a string
    def getInventoryYaml(self):
        return yaml.dump(self.getInventory(), default_flow_style=False)

    # Gets a tag in the database
    # @param name       The name of the tag to get
    # @return           The Tag object, or None if the tag does
    #                   not exist.
    def getTag(self, name):
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM Tag WHERE TagName = %s",
                [name])

        row = cursor.fetchone()
        if row == None:
            return None

        tag = Tag(row[0], row[1], row[2], row[3], 
                self)
        cursor.fetchall()
        cursor.close()
        return tag

    # Gets all the tag groups in the database and which tags
    # belong to them.
    # @return   A list of (group, tagnames) tuples where tagnames
    #           is a comma separated list of tags in the group.
    def getTagGroups(self):
        groups = list()

        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM TagByGroup ORDER BY TagGroup ASC")
        for (groupName, tags) in cursor:
            group = groupName if groupName != None else 'ungrouped'
            groups.append( (group, tags) )
        cursor.close()

        return groups

    # Gets all the tags in the database
    # @param groupSort=False    If true, sort the tags first by
    #                           group name and then by tag name.
    #                           Otherwise just sort by tag name.
    # @return   An array containing all the tags in the database
    def getTags(self, groupSort=False):
        tags = list()

        # Build statement
        stmt = "SELECT * FROM Tag "
        if groupSort == True:
            stmt += 'ORDER BY TagGroup ASC, TagName ASC'
        else:
            stmt += 'ORDER BY TagName ASC'

        # Fetch data
        cursor = self._conn.cursor()
        cursor.execute(stmt)
        for (tagId, name, group, description) in cursor:
            tag = Tag(tagId, name, group, description, self)
            tags.append(tag)
        cursor.close()

        return tags

    # Gets the libIsidore version
    # @return       The libIsidore version
    def getVersion(self):
        return self._version

class Host:

    _hostId = None
    _hostname = None
    _commissionDate = None
    _decommissionDate = None
    _description = None
    _isidore = None

    def __init__(self, hostId, hostname, commissionDate, decommissionDate, description, isidore=None):
        self._hostId = hostId
        self._hostname = hostname
        self._commissionDate = commissionDate
        self._decommissionDate = decommissionDate
        self._description = description
        self._isidore = isidore

    def addTag(self, tag):
        cursor = self._isidore._conn.cursor()
        stmt = "INSERT INTO HostHasTag (HostID, TagID) VALUES (%s, %s)"
        cursor.execute(stmt, [ self._hostId, tag.getTagId() ])
        self._isidore._conn.commit()
        cursor.close()

    def getHostId(self):
        return self._hostId

    def getHostname(self):
        return self._hostname

    def getCommissionDate(self):
        return self._commissionDate

    def getDecommissionDate(self):
        return self._decommissionDate

    # Gets a dictionary containing all the details about this host
    # @return   A dictionary containing the details
    def getDetails(self):
        det = {}
        det[self._hostname] = {}
        det[self._hostname]['vars'] = {}
        isivar = {}

        # Host Attributes
        isivar['commissioned'] = str(self._commissionDate) \
                if self._commissionDate is not None else None
        isivar['decommissioned'] = str(self._decommissionDate) \
                if self._decommissionDate is not None else None
        isivar['description'] = self._description

        # Tags
        isivar['tags'] = {}
        for tag in self.getTags(True):
            group = tag.getGroup() if tag.getGroup() is not None else 'ungrouped'

            if group not in isivar['tags']:
                isivar['tags'][group] = list()

            isivar['tags'][group].append(tag.getName())

        det[self._hostname]['vars']['isidore'] = isivar
        return det

    def getDescription(self):
        return self._description

    # Gets all the tags assigned to this host
    # @param groupSort=False    If true, sort the tags first by
    #                           group name and then by tag name.
    #                           Otherwise just sort by tag name.
    # @return   An array containing all the tags assigned to this
    #           host
    def getTags(self, groupSort=False):
        tags = list()

        stmt = '''\
            SELECT
                Tag.TagID,
                TagName,
                TagGroup,
                Description
            FROM Tag
            INNER JOIN HostHasTag
                ON Tag.TagID = HostHasTag.TagID
            WHERE HostID = %s
            '''

        if groupSort == True:
            stmt += 'ORDER BY TagGroup ASC, TagName ASC'
        else:
            stmt += 'ORDER BY TagName ASC'

        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [self._hostId])
        for (tagId, name, group, description) in cursor:
            tag = Tag(tagId, name, group, description)
            tags.append(tag)
        cursor.close()

        return tags

    def removeTag(self, tag):
        cursor = self._isidore._conn.cursor()
        stmt = '''\
            DELETE FROM HostHasTag
            WHERE 
                HostID = %s AND
                TagId = %s
            '''
        cursor.execute(stmt, [ self._hostId, tag.getTagId() ])
        self._isidore._conn.commit()
        cursor.close()

    def setCommissionDate(self, date):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Host SET CommissionDate = %s WHERE HostID = %s"
        cursor.execute(stmt, [ date, self._hostId ])
        self._isidore._conn.commit()
        cursor.close()
        self._commissionDate = date

    def setDecommissionDate(self, date):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Host SET DecommissionDate = %s WHERE HostID = %s"
        cursor.execute(stmt, [ date, self._hostId ])
        self._isidore._conn.commit()
        cursor.close()
        self._decommissionDate = date

    def setDescription(self, description):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Host SET Description = %s WHERE HostID = %s"
        cursor.execute(stmt, [ description, self._hostId ])
        self._isidore._conn.commit()
        cursor.close()
        self._description = description

    def setHostname(self, hostname):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Host SET Hostname = %s WHERE HostID = %s"
        cursor.execute(stmt, [ hostname, self._hostId ])
        self._isidore._conn.commit()
        cursor.close()
        self._hostname = hostname

class Tag:
    
    _tagId = None
    _name = None
    _group = None
    _description = None
    _isidore = None

    def __init__(self, tagId, name, group, description,
            isidore=None):
        self._tagId = tagId
        self._name = name
        self._group = group
        self._description = description
        self._isidore = isidore

    def getTagId(self):
        return self._tagId

    def getName(self):
        return self._name

    def getDescription(self):
        return self._description

    # Gets a dictionary containing all the details about this tag
    # @return   A dictionary containing the details
    def getDetails(self):
        det = {}
        det[self._name] = {}
        det[self._name]['vars'] = {}
        isivar = {}
        hosts = list()

        # Tag Attributes
        isivar['description'] = self._description
        isivar['group'] = self._group

        # Hosts
        for host in self.getHosts():
            hosts.append(host.getHostname())

        det[self._name]['vars']['isidore'] = isivar
        det[self._name]['hosts'] = hosts
        return det

    def getGroup(self):
        return self._group

    # Gets all the commissioned hosts assigned to this tag
    # @return   An array containing all the commissioned hosts
    #           assigned to this tag
    def getHosts(self):
        hosts = list()

        stmt = '''\
            SELECT
                Host.HostID,
                Hostname,
                CommissionDate,
                DecommissionDate,
                Description
            FROM Host
            INNER JOIN HostHasTag
                ON Host.HostID = HostHasTag.HostID
            WHERE
                TagID = %s AND
                DecommissionDate IS NULL
            ORDER BY Hostname ASC
            '''

        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [self._tagId])
        for (hostId, hostname, commissionDate, decommissionDate, description) in cursor:
            host = Host(hostId, hostname, commissionDate,
                    decommissionDate, description, self)
            hosts.append(host)
        cursor.close()

        return hosts

    def setDescription(self, description):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Tag SET Description = %s WHERE TagID = %s"
        cursor.execute(stmt, [ description, self._tagId ])
        self._isidore._conn.commit()
        cursor.close()
        self._description = description

    def setGroup(self, group):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Tag SET TagGroup = %s WHERE TagID = %s"
        cursor.execute(stmt, [ group, self._tagId ])
        self._isidore._conn.commit()
        cursor.close()
        self._group = group

    def setName(self, name):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Tag SET TagName = %s WHERE TagID = %s"
        cursor.execute(stmt, [ name, self._tagId ])
        self._isidore._conn.commit()
        cursor.close()
        self._name = name

