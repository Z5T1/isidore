# 9. Configuring the Isidore Installation

1. [Overview](#1-overview)
2. [Querying Information About the Installation](#2-querying-information-about-the-installation)
   1. [Database Connection Information](#1-database-connection-information)
   2. [Version Information](#2-version-information)
3. [Message of the Day](#3-message-of-the-day)

## 1. Overview

There are various parameters of the global Isidore that can be configured from
the command line. These paramenters are modified via the `config` subprompt.
From the config subprompt, the parameters can be configured and queried using
the `set` and `show` commands respectively. One can think of working with these
parameters as akin to interacting with [variables](variables.md) that affect
the whole Isidore installation.

## 2. Querying Information About the Installation

### 1. Database Connection Information

Information about the SQL database connection can be displayed by issuing the
`show connection` command from the config subprompt. It displays the following
information:

| Field    | Description                                 |
| -------- | ------------------------------------------- |
| database | The name of the installation's SQL database |
| host     | The SQL server                              |
| user     | The SQL user                                |

### 2. Version Information

Information about the Isidore version can be displayed by issuing the `show
version` command from the config subprompt. It displays the following
information:

| Field                          | Description                                          |
| ------------------------------ | ---------------------------------------------------- |
| Isidore Command Prompt version | The version of the Isidore comand prompt binary      |
| libIsidore version             | The version of the underlying Isidore Python library |
| Isidore database version       | The version of the Isidore SQL database              |

In order for the Isidore installation to be functional, the command prompt,
library, and database versions MUST be of the same major version. For the minor
version and patch release, the following constraint MUST be satisfied:

command prompt >= library >= database

Note that the library and database versions SHOULD be the same as the internal
database structure is not considered part of the public API. A library version
with a minor version or patch release number greater than the database version
may or may not work depending on the specific combination.

## 3. Message of the Day

The message of the day is displayed whenever the Isidore command line is
started at the root prompt (`> `). It is not displayed when a subprompt is
specified as a command line argument (i.e. `isidore show`).

The message of the day can be set using the `config set motd <message>`
command. It can be displayed using the `config show motd` command.

