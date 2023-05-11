# 8. Maintenance

1. [Upgrading Isidore](#1-upgrading)
   1. [Export the Current Configuration](#1-export-the-current-configuration)
   2. [Upgrade the Database](#2-upgrade-the-database)
   3. [Upgrade libIsidore and the Isidore Command Prompt](#3-upgrade-libisidore-and-the-isidore-command-prompt)
   4. [Import the Current Configuration](#4-import-the-current-configuration)

## 1. Upgrading Isidore

The process for upgrading Isidore is broken down into the following steps:

1. Export the Current Configuration
2. Upgrade the Database
3. Upgrade libIsidore and the Isidore Command Prompt
4. Import the Current Configuration

There is no guarantee that the Isidore SQL database will remain stable at any
point. It should not be considered part of the public API. As such, you must
make no assumptions about the integrity of the database from one version to the
next. Only libIsidore and the Isidore Command Prompt are considered to be part
of the stable API. You should use them exclusively when interacting with
Isidore.

### 1. Export the Current Configuration

Prior to upgrading the database, export the current configuration. **This step
is extremely important!** Step 2 (upgrading the database) will delete
everything in your database. This is the only way to preserve your data when
upgrading Isidore.

Export the database using the following command:

    solo@han:~$ isidore <<< "show config" > isidore_config.txt

Inspect the file to ensure that the export was successful. It should have a
bunch of Isidore commands starting with something similar to the following:

    create host 'beru'
    host 'beru' set commissioned '2023-05-04 10:46:50'
    host 'beru' set decommissioned '1977-05-25 00:00:00'
    host 'beru' set description 'none'

### 2. Upgrade the Database

**Do not perform this step until you have completed step 1 successfully!**

Navigate to the top level of the Isidore source directory. Then connect to the
MySQL server. Replace USER, HOST, and DATABASE with the values specified in
your `isidore.cfg`.

    solo@han:~/isidore$ mysql -u USER -h HOST -p DATABASE

When prompted, enter the database password set in `isidore.cfg`.

Next source the `create_db.sql` script (in the `db` directory) to delete all
your current data and create the new tables.

    MariaDB [isidore]> SOURCE db/create_db.sql

Ensure that all of the queries exit with `OK`.

### 3. Upgrade libIsidore and the Isidore Command Prompt

Next upgrade the Isidore libraries and binaries. Run the following from the
root of the Isidore source tree. If you installed Isidore to a nonstandard
location, make sure to specify the `DESTDIR` Make variable like you did when
you [installed Isidore](install.md#1-copy-the-required-files).

    solo@han:~/isidore$ make install

Ensure that all the Isidore components have been upgraded successfully by
running the following command:

    solo@han:~$ isidore <<< "version"

The output should indicate the version of Isidore you are upgrading *to* for
all of the version fields. For example, the following is the expected output
when upgrading version 0.1.1:

    Isidore Command Prompt version: 0.1.1
    libIsidore version: 0.1.1
    Isidore database version: 0.1.1

### 4. Import the Current Configuration

Finally, import your data back into Isidore using the following command:

    solo@han:~$ isidore < isidore_config.txt

