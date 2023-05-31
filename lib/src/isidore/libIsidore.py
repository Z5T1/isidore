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

import os
import configparser

import mysql.connector
import yaml
import json

# Represents an Isidore database instance
class Isidore:

    _conn = None
    _version = '0.1.5'

    # Connects to a MySQL database and creates a new Isidore object to interact
    # with it.
    # @param user       The MySQL username
    # @param password   The password for the MySQL user
    # @param host       The MySQL server to connect to
    # @param database   The name of the database to use
    def __init__(self, user, password, host, database):
        self._conn = mysql.connector.connect(
                user = user,
                password = password,
                host = host,
                database = database
        )

    # Loads the database credentials from a file. It then connects to the MySQL
    # database specified by the config and creates a new Isidore object to
    # interact with it.
    #
    # If no file is specified, the standard Isidore system config files will be
    # tried in the following order. Any variables set in a file that is further
    # down the list will take precedence over anything set in a file higher up
    # the list.
    # - /etc/isidore.cfg
    # - /usr/local/etc/isidore.cfg
    # - ~/.isidore.cfg
    # - ./isidore.cfg
    #
    # @param file       The path to the file to load, or None to use the system
    #                   configuration.
    @classmethod
    def fromConfigFile(cls, file=None):

        # Read config file
        config = configparser.ConfigParser()
        if file == None:
            config.read( [
                "/etc/isidore.cfg",
                "/usr/local/etc/isidore.cfg",
                os.path.expanduser("~/.isidore.cfg"),
                "isidore.cfg"
                ] )
        else:
            config.read( [ file ] )

        # Set the required variables
        user = config['database']['user']
        password = config['database']['password']
        host = config['database']['host']
        database = config['database']['database']

        # Make the MySQL connection
        return cls(user, password, host, database)

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
        cursor.execute('''
                SELECT
                    HostID,
                    Hostname,
                    CommissionDate,
                    DecommissionDate,
                    Description
                FROM Host
                WHERE DecommissionDate IS NULL
                ORDER BY Hostname ASC''')
        for (hostId, hostname, commissionDate, decommissionDate, description) in cursor:
            host = Host(hostId, hostname, commissionDate,
                    decommissionDate, description, self)
            hosts.append(host)
        cursor.close()

        return hosts

    # Gets the underlying Isidore database version.
    # @return       The Isidore database version
    def getDatabaseVersion(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT Value FROM Metadata WHERE KeyName = 'version'")
        row = cursor.fetchone()
        cursor.close()
        return row[0]

    # Gets all the decommissioned hosts in the database
    # @return   An array containing all the decommissioned hosts in
    #           the database
    def getDecommissionedHosts(self):
        hosts = list()

        cursor = self._conn.cursor()
        cursor.execute('''
                SELECT
                    HostID,
                    Hostname,
                    CommissionDate,
                    DecommissionDate,
                    Description
                FROM Host
                WHERE DecommissionDate IS NOT NULL
                ORDER BY Hostname ASC''')
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
        cursor.execute('''
                SELECT
                    HostID,
                    Hostname,
                    CommissionDate,
                    DecommissionDate,
                    Description
                FROM Host
                WHERE Hostname = %s''',
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
        cursor.execute('''
                SELECT
                    HostID,
                    Hostname,
                    CommissionDate,
                    DecommissionDate,
                    Description
                FROM Host
                ORDER BY Hostname ASC''')
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
        # Any variables assigned to the 'all' tag require special treatment
        # since it goes at the top of the YAML tree unlike all the other tags.
        tag_all = self.getTag('all')
        inv = {
                'all': {
                    'hosts': dict(),
                    'children': dict(),
                    'vars': dict() if tag_all == None
                        else tag_all.getDetails()['all']['vars']
                }
        }

        # Add all the hosts without a group to ensure every system is included,
        # even those without any tags.
        for host in self.getCommissionedHosts():
            name = host.getHostname()
            inv['all']['hosts'][name] = host.getDetails()[name]['vars']

        # Add each tag and its hosts as a group
        for tag in self.getTags(True):
            name = tag.getName()
            details = tag.getDetails()
            # Skip the all tag since it requires special care and is handled
            # above
            if name == 'all':
                continue
            inv['all']['children'][name] = {
                    'hosts': dict.fromkeys(details[name]['hosts'], dict()),
                    'vars': details[name]['vars']
            }

        # Generate YAML output without any anchors/aliases
        noalias_dumper = yaml.dumper.SafeDumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        return yaml.dump(inv, default_flow_style=False, Dumper=noalias_dumper)

    # Gets a tag in the database
    # @param name       The name of the tag to get
    # @return           The Tag object, or None if the tag does
    #                   not exist.
    def getTag(self, name):
        cursor = self._conn.cursor()
        cursor.execute('''
            SELECT
                TagId,
                TagName,
                TagGroup,
                Description
            FROM Tag
            WHERE TagName = %s''',
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
        stmt = '''
            SELECT
                TagId,
                TagName,
                TagGroup,
                Description
            FROM Tag '''
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

    # Gets a dictionary of all the tags in the database broken down into
    # groups. The tag group will be the top level key in the dictionary and
    # each key's value will a list containing all the tags in that group.
    # @return   A dictionary containing all the tags in the database
    def getTagsByGroup(self):
        tags = {}

        # Build statement
        stmt = '''
            SELECT 
                TagId,
                TagName,
                TagGroup,
                Description
            FROM Tag '''
        if groupSort == True:
            stmt += 'ORDER BY TagGroup ASC, TagName ASC'
        else:
            stmt += 'ORDER BY TagName ASC'

        # Fetch data
        cursor = self._conn.cursor()
        cursor.execute(stmt)
        for (tagId, name, group, description) in cursor:
            tag = Tag(tagId, name, group, description, self)

            if group == None:
                group = 'ungrouped'
            if group not in tags:
                tags[group] = list()

            tags[group].append(tag)
        cursor.close()

        return tags

    # Gets the libIsidore version
    # @return       The libIsidore version
    def getVersion(self):
        return self._version

# An individual host
class Host:

    _hostId = None
    _hostname = None
    _commissionDate = None
    _decommissionDate = None
    _description = None
    _isidore = None

    # Creates a new Host object
    # @param hostId             The Isidore databases's internal ID for the host
    # @param hostname           The hostname for the host
    # @param commissionDate     The host's commission date
    # @param decommissionDate   The host's decommission date
    # @param description        The host's description
    # @param isidore            The Isidore object the host belongs to
    def __init__(self, hostId, hostname, commissionDate, decommissionDate, description, isidore=None):
        self._hostId = hostId
        self._hostname = hostname
        self._commissionDate = commissionDate
        self._decommissionDate = decommissionDate
        self._description = description
        self._isidore = isidore

    # Assigns a tag to this host
    # @param tag        The tag object to assign
    def addTag(self, tag):
        cursor = self._isidore._conn.cursor()
        stmt = "INSERT INTO HostHasTag (HostID, TagID) VALUES (%s, %s)"
        cursor.execute(stmt, [ self._hostId, tag.getTagId() ])
        self._isidore._conn.commit()
        cursor.close()

    # Appends an item to a list variable
    # @param path       The path of the list to append to.
    # @param value      The value to append to the list. This can
    #                   be of any type that is JSON serializable.
    def appendVar(self, path, value):
        # Ensure the path starts with $
        if path[0] != '$':
            path = '$.' + path

        # Set the variable
        stmt = '''
            UPDATE Host
            SET Variables =
                JSON_ARRAY_APPEND(
                    (SELECT Variables
                        FROM (SELECT * FROM Host) AS temp
                        WHERE HostId = %s),
                    %s,
                    JSON_EXTRACT(%s, '$')
                )
            WHERE HostID = %s'''
        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [
            self._hostId,
            path,
            json.dumps(value),
            self._hostId])
        self._isidore._conn.commit()
        cursor.close()

    # Deletes this host from the database. The host object should
    # not be referenced after this method is called.
    def delete(self):
        # Delete the host
        cursor = self._isidore._conn.cursor()
        stmt = "DELETE FROM Host WHERE HostID = %s"
        cursor.execute(stmt, [ self._hostId ])
        self._isidore._conn.commit()
        cursor.close()

        # Blank out all the fields in case the object is
        # referenced again.
        self._hostId = None
        self._hostname = None
        self._commissionDate = None
        self._decommissionDate = None
        self._description = None
        self._isidore = None

    # Gets the host's internal ID in the Isidore database.
    # @return   The hosts's ID
    def getHostId(self):
        return self._hostId

    # Gets the host's hostname
    # @return   The hostname
    def getHostname(self):
        return self._hostname

    # Gets the host's commission date as a DateTime
    # @return   The commission date
    def getCommissionDate(self):
        return self._commissionDate

    # Gets the host's decommission date as a DateTime
    # @return   The decommission date, or None if the host is commissioned.
    def getDecommissionDate(self):
        return self._decommissionDate

    # Gets a dictionary containing all the details about this host
    # @return   A dictionary containing the details
    def getDetails(self):
        det = {}
        det[self._hostname] = {}
        det[self._hostname]['vars'] = self.getVar()
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

    # Gets the host's description
    # @return   The host's description
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

    # Gets a dictionary of variables assigned to this host,
    # optionally starting at a certian path. Paths should be
    # specified as path.to.object. If no path is specified, all
    # variables will be included.
    # @param path       The path to start at. If not specifed,
    #                   defaults to the root of the JSON tree.
    # @return   A dictionary containing all the variables starting
    #           at path.
    def getVar(self, path='$'):
        # Ensure the path starts with $
        if path[0] != '$':
            path = '$.' + path

        # Select the JSON
        stmt = 'SELECT JSON_EXTRACT(Variables, %s) \
                FROM Host WHERE HostID = %s'
        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [path, self._hostId])
        row = cursor.fetchone()
        cursor.close()

        # Decode the JSON and return
        if row[0] == None:
            return None
        else:
            return json.loads(row[0])

    # Removes a tag from this host
    # @param tag        The tag object to remove
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

    # Sets the host's commission date
    # @param date       The commission date
    def setCommissionDate(self, date):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Host SET CommissionDate = %s WHERE HostID = %s"
        cursor.execute(stmt, [ date, self._hostId ])
        self._isidore._conn.commit()
        cursor.close()
        self._commissionDate = date

    # Sets the host's decommission date
    # @param date       The decommission date, or None to clear the
    #                   decommission date.
    def setDecommissionDate(self, date):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Host SET DecommissionDate = %s WHERE HostID = %s"
        cursor.execute(stmt, [ date, self._hostId ])
        self._isidore._conn.commit()
        cursor.close()
        self._decommissionDate = date

    # Sets the host's description
    # @param description    The host's description
    def setDescription(self, description):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Host SET Description = %s WHERE HostID = %s"
        cursor.execute(stmt, [ description, self._hostId ])
        self._isidore._conn.commit()
        cursor.close()
        self._description = description

    # Sets the host's hostname
    # @param hostname       The hostname
    def setHostname(self, hostname):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Host SET Hostname = %s WHERE HostID = %s"
        cursor.execute(stmt, [ hostname, self._hostId ])
        self._isidore._conn.commit()
        cursor.close()
        self._hostname = hostname

    # Sets a variable to a specified value.
    # @param path       The path of the variable to set. It will
    #                   be created if it does not exist. If it is
    #                   not specifed or is $, the entire variable
    #                   tree will be overwritten with the
    #                   specified value.
    # @param value      The value to set the variable to. This can
    #                   be of any type that is JSON serializable.
    def setVar(self, path, value):
        # Ensure the path starts with $
        if path[0] != '$':
            path = '$.' + path

        # Set the variable
        stmt = '''
            UPDATE Host
            SET Variables =
                JSON_SET(
                    Variables,
                    %s,
                    JSON_EXTRACT(%s, '$')
                )
            WHERE HostID = %s'''
        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [path, json.dumps(value), self._hostId])
        self._isidore._conn.commit()
        cursor.close()

    # Unsets a variable.
    # @param path       The path of the variable to unset.
    def unsetVar(self, path):
        # Ensure the path starts with $
        if path[0] != '$':
            path = '$.' + path

        # Set the variable
        stmt = '''
            UPDATE Host
            SET Variables =
                JSON_REMOVE(
                    Variables,
                    %s
                )
            WHERE HostID = %s'''
        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [path, self._hostId])
        self._isidore._conn.commit()
        cursor.close()

# An individual tag
class Tag:
    
    _tagId = None
    _name = None
    _group = None
    _description = None
    _isidore = None

    # Creates a new Tag Object
    # @param tagID              The Isidore databases's internal ID for the tag
    # @param name               The name of the tag
    # @param group              The group for the tag
    # @param description        The tag's description
    # @param isidore            The Isidore object the tag belongs to
    def __init__(self, tagId, name, group, description,
            isidore=None):
        self._tagId = tagId
        self._name = name
        self._group = group
        self._description = description
        self._isidore = isidore

    # Appends an item to a list variable
    # @param path       The path of the list to append to.
    # @param value      The value to append to the list. This can
    #                   be of any type that is JSON serializable.
    def appendVar(self, path, value):
        # Ensure the path starts with $
        if path[0] != '$':
            path = '$.' + path

        # Set the variable
        stmt = '''
            UPDATE Tag
            SET Variables =
                JSON_ARRAY_APPEND(
                    (SELECT Variables
                        FROM (SELECT * FROM Tag) AS temp
                        WHERE TagId = %s),
                    %s,
                    JSON_EXTRACT(%s, '$')
                )
            WHERE TagID = %s'''
        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [
            self._tagId,
            path,
            json.dumps(value),
            self._tagId])
        self._isidore._conn.commit()
        cursor.close()

    # Deletes this tag from the database. The tag object should
    # not be referenced after this method is called.
    def delete(self):
        # Delete the tag
        cursor = self._isidore._conn.cursor()
        stmt = "DELETE FROM Tag WHERE TagID = %s"
        cursor.execute(stmt, [ self._tagId ])
        self._isidore._conn.commit()
        cursor.close()

        # Blank out all the fields in case the object is
        # referenced again.
        self._tagId = None
        self._name = None
        self._group = None
        self._description = None
        self._isidore = None

    # Gets the tag's internal ID in the Isidore database.
    # @return   The tag's ID
    def getTagId(self):
        return self._tagId

    # Gets the tag's name
    # @return   The name
    def getName(self):
        return self._name

    # Gets the tag's description
    # @return   The tag's description
    def getDescription(self):
        return self._description

    # Gets a dictionary containing all the details about this tag
    # @return   A dictionary containing the details
    def getDetails(self):
        det = {}
        det[self._name] = {}
        det[self._name]['vars'] = self.getVar()
        isivar = {}
        hosts = list()

        # Tag Attributes
        isivar['description'] = self._description
        isivar['group'] = self._group

        # Hosts
        for host in self.getHosts():
            hosts.append(host.getHostname())

        det[self._name]['vars']['isidore_tag_'+self._name] = isivar
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

    # Gets a dictionary of variables assigned to this tag,
    # optionally starting at a certian path. Paths should be
    # specified as path.to.object. If no path is specified, all
    # variables will be included.
    # @param path       The path to start at. If not specifed,
    #                   defaults to the root of the JSON tree.
    # @return   A dictionary containing all the variables starting
    #           at path.
    def getVar(self, path='$'):
        # Ensure the path starts with $
        if path[0] != '$':
            path = '$.' + path

        # Select the JSON
        stmt = 'SELECT JSON_EXTRACT(Variables, %s) \
                FROM Tag WHERE TagID = %s'
        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [path, self._tagId])
        row = cursor.fetchone()
        cursor.close()

        # Decode the JSON and return
        if row[0] == None:
            return None
        else:
            return json.loads(row[0])

    # Sets the tag's description
    # @param description    The tag's description
    def setDescription(self, description):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Tag SET Description = %s WHERE TagID = %s"
        cursor.execute(stmt, [ description, self._tagId ])
        self._isidore._conn.commit()
        cursor.close()
        self._description = description

    # Sets the tag's group
    # @param group          The group for the tag, or None to remove it from
    #                       its current group.
    def setGroup(self, group):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Tag SET TagGroup = %s WHERE TagID = %s"
        cursor.execute(stmt, [ group, self._tagId ])
        self._isidore._conn.commit()
        cursor.close()
        self._group = group

    # Set the tag's name
    # @param name           The name
    def setName(self, name):
        cursor = self._isidore._conn.cursor()
        stmt = "UPDATE Tag SET TagName = %s WHERE TagID = %s"
        cursor.execute(stmt, [ name, self._tagId ])
        self._isidore._conn.commit()
        cursor.close()
        self._name = name

    # Sets a variable to a specified value.
    # @param path       The path of the variable to set. It will
    #                   be created if it does not exist. If it is
    #                   not specifed or is $, the entire variable
    #                   tree will be overwritten with the
    #                   specified value.
    # @param value      The value to set the variable to. This can
    #                   be of any type that is JSON serializable.
    def setVar(self, path, value):
        # Ensure the path starts with $
        if path[0] != '$':
            path = '$.' + path

        # Set the variable
        stmt = '''
            UPDATE Tag
            SET Variables =
                JSON_SET(
                    Variables,
                    %s,
                    JSON_EXTRACT(%s, '$')
                )
            WHERE TagID = %s'''
        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [path, json.dumps(value), self._tagId])
        self._isidore._conn.commit()
        cursor.close()

    # Unsets a variable.
    # @param path       The path of the variable to unset.
    def unsetVar(self, path):
        # Ensure the path starts with $
        if path[0] != '$':
            path = '$.' + path

        # Set the variable
        stmt = '''
            UPDATE Tag
            SET Variables =
                JSON_REMOVE(
                    Variables,
                    %s
                )
            WHERE TagID = %s'''
        cursor = self._isidore._conn.cursor()
        cursor.execute(stmt, [path, self._tagId])
        self._isidore._conn.commit()
        cursor.close()

