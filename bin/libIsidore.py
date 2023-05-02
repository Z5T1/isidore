#!/usr/bin/env python3

import mysql.connector

class Isidore:

    def __init__(self, user, password, host, database):
        self.conn = mysql.connector.connect(
                user = user,
                password = password,
                host = host,
                database = database
        )

    # Gets all the hosts in the database
    # @return   An array containing all the hosts in the database
    def getHosts(self):
        hosts = list()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Host")
        for (hostId, hostname, commissionDate, decommissionDate, description) in cursor:
            host = Host(hostId, hostname, commissionDate, decommissionDate, description)
            hosts.append(host)
        cursor.close()

        return hosts

    # Gets all the tags in the database
    # @return   An array containing all the tags in the database
    def getTags(self):
        tags = list()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Tag")
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

    def __init__(self, hostId, hostname, commissionDate, decommissionDate, description):
        self.hostId = hostId
        self.hostname = hostname
        self.commissionDate = commissionDate
        self.decommissionDate = decommissionDate
        self.description = description

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

class Tag:
    
    tagId = None
    name = None
    group = None
    description = None

    def __init__(self, tagId, name, group, description):
        self.tagId = tagId
        self.name = name
        self.group = group
        self.description = description

    def getTagId(self):
        return self.tagId

    def getName(self):
        return self.name

    def getGroup(self):
        return self.group

    def getDescription(self):
        return self.description

