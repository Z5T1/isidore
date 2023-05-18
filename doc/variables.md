# 7. Variables

1. [Overview of Variables in Isidore](#1-overview-of-variables-in-isidore)
2. [Setting Variables](#2-setting-variables)
   1. [Set Examples](#1-set-examples)
3. [Displaying Variables](#3-displaying-variables)
   1. [Display Examples](#1-display-examples)
4. [Appending to List Variables](#4-appending-to-list-variables)
5. [Unsetting Variables](#5-unsetting-variables)

## 1. Overview of Variables in Isidore

Traditionally, Ansible variables are set either in the inventory or in separate
`host_vars` and `group_vars` directories. While the latter approach will work
with Isidore without issue and may be preferable in some environments, Isidore
also has its own variable management system. This allows for central management
all your Ansible variables along with you inventory.

Variables can be set at two levels in Isidore: the host level and the tag
level. If the same variable is set at both levels, the value that is set at the
host level will take precedence over the value that's set at the tag level.

Ansible variables are organized heirarchically. As such, each host and tag has
its own variable tree and supports sub variables, lists, and dictionaries.

## 2. Setting Variables

Variables are set using the `var set` command from either the host or tag
subprompt. The syntax is `var set <variable_name> <value>`.

The `<variable_name>` parameter can contain periods or brackets to reference
subelements or array indicies. The path of the variable is always taken
relative to the root of the variable tree. To set the entire variable tree,
specify `$` as the `<variable_name>`.

The `<value>` parameter can be anything that is valid JSON, including objects,
arrays, and complex JSON trees.

### 1. Set Examples

For example, to set host `yoda`'s `age` variable to `900` use the following:

    host yoda> var set age 900

To set host `yoda`'s `instursion_prevention_system variable` to `lightsaber`,
use the following:

    host yoda> var set intrusion_prevention_system '"lightsaber"'

To set host `chewy`'s `age` variable to `200` and `instursion_prevention_system`
variable to `crossbow` in one line use the following. Note that this will clear
any other variables that are set as it sets the entire variable tree.

    host chewy> var set $ '{"age": 200, "intrusion_prevention_system": "crossbow"}'

To set tag `cherryhill`'s `county` variable to `Camden`:

    tag cherryhill> var set county '"Camden"'

## 3. Displaying Variables

Variables are displayed using the `var print` subcommand at either the host or
tag subprompt. The syntax is `var print [variable_name]`. If `[variable_name]`
is ommitted, it will print the entire variable tree. This is identical to
specifying `[variable_name]` as `$`. Like with `var set`, periods and brackets
can be used to specify sublevels of the variable tree. The output is printed in
YAML by default.

### 1. Display Examples

To display all of the variables assigned to the host `yoda`, use the following:

    host yoda> var print
    age: 900
    intrusion_prevention_system: lightsaber
    
    host yoda>

To display the `intrusion_prevention_system` for the host `chewy`:

    host chewy> var print intrusion_prevention_system
    crossbow
    ...
    
    host chewy>

To display all of the variables assigned to the `cherryhill` tag:

    tag cherryhill> var print
    county: Camden
    
    tag cherryhill>

## 4. Appending to List Variables

For variables of the list type, it is possible to append values to them using
the `var append` command from either the host or tag subprompt. The syntax is
`var append <variable_name> <value>`.

The variable name should be specified the same as it would for the `var set`
command. As with `var set`, `<value>` can be anything that is valide JSON.

For example, to append the string item `new item` to the variable named
`test_list`, use the following:

    host yoda> var append test_list '"new item"'

## 5. Unsetting Variables

Variables can be unset using the `var unset` command from either the host or
tag subprompt. This effectively deletes the variable and any children it may
have. The syntax is `var unset <variable_name>`. The variable name should be
specified the same as it would for the `var set` command.

For example, to unset the `age` variable:

    host yoda> var unset age

