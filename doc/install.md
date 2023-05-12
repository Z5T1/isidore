Installation
============

Overview
--------

This section documents how to install Isidore.

System Requirements
-------------------

### Required Packages

The following versions or higher of the following packages are required:

* Python 3.7
* Either MariaDB 10.3 or MySQL 8.0

Assumptions
-----------

This guide makes the following assumptions. If any of these are not true, take
care to change the specified values as necessary.

1. Your MariaDB/MySQL server is `localhost`.
2. The database you wish to use will be named `isidore`.
3. The user you wish to use to access the database will be named `isidore`.
4. You are installing to `/opt/isidore`.

Installation
------------

Installation is broken down into the following steps.

1. Copy the Required Files
2. Create the Database
3. Configure the Isidore Command Prompt
4. Start the Isidore Command Prompt

Unless otherwise noted, all commands should be run from the top level of the
Isidore source directory.

### 1. Copy the Required Files

Install the binaries and associated documentation. 

#### Installation Directory

Isidore uses a non-standard directory structure, so by default it installs to
`/opt/isidore`. This directory can be changed by setting the `DESTDIR` variable
via either the environment or an additional argument to the `make` command.

#### Perform the Installation

If you are performing a system wide installation (which is the default), the
following commands will need to be run with root privileges:

Install the binaries and documentation using the provided Makefile:

    make install

Install the required Python packages:

    pip3 install -r requirements.txt

### 2. Create the Database

Connect to your MySQL server:

    mysql -u root -p

Enter your MySQL root password when prompted.

Create the database:

    MariaDB [(none)]> CREATE DATABASE isidore;

Create the MySQL user and grant him access to the database:

    MariaDB [(none)]> CREATE USER 'isidore'@'localhost'
        -> IDENTIFIED BY 'ChangeThisToAMoreSecurePassword';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON isidore.* TO 'isidore'@'localhost';
    MariaDB [(none)]> FLUSH PRIVILEGES;

Populate the database with the initial tables:

    MariaDB [(none)]> USE isidore;
    MariaDB [(isidore)]> SOURCE db/create_db.sql;

Quit the MySQL prompt:

    MariaDB [(isidore)]> QUIT;

### 3. Configure the Isidore Command Prompt

Determine where you would like the config file to reside. You have a few
options. They are listed below from lowest to highest precedence:

1. /etc/isidore.cfg
2. /usr/local/etc/isidore.cfg
3. ~/.isidore.cfg
4. ./isidore.cfg

For the sake of this guide, /etc/isidore.cfg will be used.

Copy over the provided sample config file:

    cp isidore.cfg.sample /etc/isidore.cfg

Using your favorite text editor, open up this file and change the `password`
field under the `[database]` section to match the password you set in step 2.

### 4. Start the Isidore Command Prompt

You're now ready to start using Isidore. Start the Isidore command prompt using
the following command:

    /opt/isidore/bin/isidore

