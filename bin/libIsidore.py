#!/usr/bin/env python3

import mysql.connector

class Isidore:

    conn = None

    def __init__(self, user, password, host, database):
        self.conn = mysql.connector.connect(
                user = user,
                password = password,
                host = host,
                database = database
        )

    # Creates a new host in the database
    # @param hostname           The hostname for the new host
    def createHost(self, hostname):
        cursor = self.conn.cursor()
        stmt = "INSERT INTO Host (Hostname) VALUES (%s)"
        cursor.execute(stmt, [ hostname ])
        self.conn.commit()
        cursor.close()

    # Creates a new tag in the database
    # @param name               The name for the new tag
    def createTag(self, name):
        cursor = self.conn.cursor()
        stmt = "INSERT INTO Tag (TagName) VALUES (%s)"
        cursor.execute(stmt, [ name ])
        self.conn.commit()
        cursor.close()

    # Gets all the commissioned hosts in the database
    # @return   An array containing all the commissioned hosts in
    #           the database
    def getCommissionedHosts(self):
        hosts = list()

        cursor = self.conn.cursor()
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

        cursor = self.conn.cursor()
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
        cursor = self.conn.cursor()
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

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Host ORDER BY Hostname ASC")
        for (hostId, hostname, commissionDate, decommissionDate, description) in cursor:
            host = Host(hostId, hostname, commissionDate,
                    decommissionDate, description, self)
            hosts.append(host)
        cursor.close()

        return hosts

    # Gets a tag in the database
    # @param name       The name of the tag to get
    # @return           The Tag object, or None if the tag does
    #                   not exist.
    def getTag(self, name):
        cursor = self.conn.cursor()
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

    # Gets all the tags in the database
    # @return   An array containing all the tags in the database
    def getTags(self):
        tags = list()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Tag ORDER BY TagName ASC")
        for (tagId, name, group, description) in cursor:
            tag = Tag(tagId, name, group, description)
            tags.append(tag)
        cursor.close()

        return tags

class Host:

    hostId = None
    hostname = None
    commissionDate = None
    decommissionDate = None
    description = None
    isidore = None

    def __init__(self, hostId, hostname, commissionDate, decommissionDate, description, isidore=None):
        self.hostId = hostId
        self.hostname = hostname
        self.commissionDate = commissionDate
        self.decommissionDate = decommissionDate
        self.description = description
        self.isidore = isidore

    def addTag(self, tag):
        cursor = self.isidore.conn.cursor()
        stmt = "INSERT INTO HostHasTag (HostID, TagID) VALUES (%s, %s)"
        cursor.execute(stmt, [ self.hostId, tag.getTagId() ])
        self.isidore.conn.commit()
        cursor.close()

    def getHostId(self):
        return self.hostId

    def getHostname(self):
        return self.hostname

    def getCommissionDate(self):
        return self.commissionDate

    def getDecommissionDate(self):
        return self.decommissionDate

    def getDescription(self):
        return self.description

    # Gets all the tags assigned to this host
    # @return   An array containing all the tags assigned to this
    #           host
    def getTags(self):
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
            ORDER BY TagName ASC'''
        cursor = self.isidore.conn.cursor()
        cursor.execute(stmt, [self.hostId])
        for (tagId, name, group, description) in cursor:
            tag = Tag(tagId, name, group, description)
            tags.append(tag)
        cursor.close()

        return tags

    def removeTag(self, tag):
        cursor = self.isidore.conn.cursor()
        stmt = '''\
            DELETE FROM HostHasTag
            WHERE 
                HostID = %s AND
                TagId = %s
            '''
        cursor.execute(stmt, [ self.hostId, tag.getTagId() ])
        self.isidore.conn.commit()
        cursor.close()

    def setCommissionDate(self, date):
        cursor = self.isidore.conn.cursor()
        stmt = "UPDATE Host SET CommissionDate = %s WHERE HostID = %s"
        cursor.execute(stmt, [ date, self.hostId ])
        self.isidore.conn.commit()
        cursor.close()
        self.commissionDate = date

    def setDecommissionDate(self, date):
        cursor = self.isidore.conn.cursor()
        stmt = "UPDATE Host SET DecommissionDate = %s WHERE HostID = %s"
        cursor.execute(stmt, [ date, self.hostId ])
        self.isidore.conn.commit()
        cursor.close()
        self.decommissionDate = date

    def setDescription(self, description):
        cursor = self.isidore.conn.cursor()
        stmt = "UPDATE Host SET Description = %s WHERE HostID = %s"
        cursor.execute(stmt, [ description, self.hostId ])
        self.isidore.conn.commit()
        cursor.close()
        self.description = description

class Tag:
    
    tagId = None
    name = None
    group = None
    description = None
    isidore = None

    def __init__(self, tagId, name, group, description,
            isidore=None):
        self.tagId = tagId
        self.name = name
        self.group = group
        self.description = description
        self.isidore = isidore

    def getTagId(self):
        return self.tagId

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getGroup(self):
        return self.group

    # Gets all the hosts assigned to this tag
    # @return   An array containing all the hosts assigned to this tag
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
            WHERE TagID = %s
            ORDER BY Hostname ASC
            '''

        cursor = self.isidore.conn.cursor()
        cursor.execute(stmt, [self.tagId])
        for (hostId, hostname, commissionDate, decommissionDate, description) in cursor:
            host = Host(hostId, hostname, commissionDate,
                    decommissionDate, description, self)
            hosts.append(host)
        cursor.close()

        return hosts

    def setDescription(self, description):
        cursor = self.isidore.conn.cursor()
        stmt = "UPDATE Tag SET Description = %s WHERE TagID = %s"
        cursor.execute(stmt, [ description, self.tagId ])
        self.isidore.conn.commit()
        cursor.close()
        self.description = description

    def setGroup(self, group):
        cursor = self.isidore.conn.cursor()
        stmt = "UPDATE Tag SET TagGroup = %s WHERE TagID = %s"
        cursor.execute(stmt, [ group, self.tagId ])
        self.isidore.conn.commit()
        cursor.close()
        self.group = group

