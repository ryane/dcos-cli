from .common import assert_command


def test_help():
    stdout = b"""Display command line usage information

Usage:
    dcos help
    dcos help --info
    dcos help <command>

Options:
    --help     Show this screen
    --info     Show a short description of this subcommand
    --version  Show version
"""
    assert_command(['dcos', 'help', '--help'],
                   stdout=stdout)


def test_info():
    assert_command(['dcos', 'help', '--info'],
                   stdout=b'Display command line usage information\n')


def test_version():
    assert_command(['dcos', 'help', '--version'],
                   stdout=b'dcos-help version SNAPSHOT\n')


def test_list():
    stdout = """\
Command line utility for the Mesosphere Datacenter Operating
System (DCOS). The Mesosphere DCOS is a distributed operating
system built around Apache Mesos. This utility provides tools
for easy management of a DCOS installation.

Available DCOS commands:

\tconfig         \tGet and set DCOS CLI configuration properties
\thelp           \tDisplay command line usage information
\tmarathon       \tDeploy and manage applications on the DCOS
\tnode           \tManage DCOS nodes
\tpackage        \tInstall and manage DCOS software packages
\tservice        \tManage DCOS services
\ttask           \tManage DCOS tasks

Get detailed command description with 'dcos <command> --help'.
""".encode('utf-8')

    assert_command(['dcos', 'help'],
                   stdout=stdout)


def test_help_config():
    stdout = """\
Get and set DCOS CLI configuration properties

Usage:
    dcos config --info
    dcos config append <name> <value>
    dcos config prepend <name> <value>
    dcos config set <name> <value>
    dcos config show [<name>]
    dcos config unset [--index=<index>] <name>
    dcos config validate

Options:
    -h, --help       Show this screen
    --info           Show a short description of this subcommand
    --version        Show version
    --index=<index>  Index into the list. The first element in the list has an
                     index of zero

Positional Arguments:
    <name>           The name of the property
    <value>          The value of the property

""".encode('utf-8')
    assert_command(['dcos', 'help', 'config'],
                   stdout=stdout)


def test_help_marathon():
    stdout = """Deploy and manage applications on the DCOS

Usage:
    dcos marathon --config-schema
    dcos marathon --info
    dcos marathon about
    dcos marathon app add [<app-resource>]
    dcos marathon app list [--json]
    dcos marathon app remove [--force] <app-id>
    dcos marathon app restart [--force] <app-id>
    dcos marathon app show [--app-version=<app-version>] <app-id>
    dcos marathon app start [--force] <app-id> [<instances>]
    dcos marathon app stop [--force] <app-id>
    dcos marathon app update [--force] <app-id> [<properties>...]
    dcos marathon app version list [--max-count=<max-count>] <app-id>
    dcos marathon deployment list [--json <app-id>]
    dcos marathon deployment rollback <deployment-id>
    dcos marathon deployment stop <deployment-id>
    dcos marathon deployment watch [--max-count=<max-count>]
         [--interval=<interval>] <deployment-id>
    dcos marathon task list [--json <app-id>]
    dcos marathon task show <task-id>
    dcos marathon group add [<group-resource>]
    dcos marathon group list [--json]
    dcos marathon group show [--group-version=<group-version>] <group-id>
    dcos marathon group remove [--force] <group-id>
    dcos marathon group update [--force] <group-id> [<properties>...]

Options:
    -h, --help                       Show this screen

    --info                           Show a short description of this
                                     subcommand

     --json                          Print json-formatted tasks

    --version                        Show version

    --force                          This flag disable checks in Marathon
                                     during update operations

    --app-version=<app-version>      This flag specifies the application
                                     version to use for the command. The
                                     application version (<app-version>) can be
                                     specified as an absolute value or as
                                     relative value. Absolute version values
                                     must be in ISO8601 date format. Relative
                                     values must be specified as a negative
                                     integer and they represent the version
                                     from the currently deployed application
                                     definition

    --group-version=<group-version>  This flag specifies the group version to
                                     use for the command. The group version
                                     (<group-version>) can be specified as an
                                     absolute value or as relative value.
                                     Absolute version values must be in ISO8601
                                     date format. Relative values must be
                                     specified as a negative integer and they
                                     represent the version from the currently
                                     deployed group definition

    --config-schema                  Show the configuration schema for the
                                     Marathon subcommand

    --max-count=<max-count>          Maximum number of entries to try to fetch
                                     and return

    --interval=<interval>            Number of seconds to wait between actions

Positional Arguments:
    <app-id>                    The application id

    <app-resource>              Path to a file containing the app's JSON
                                definition. If omitted, the definition is read
                                from stdin. For a detailed description see
                                (https://mesosphere.github.io/
                                marathon/docs/rest-api.html#post-/v2/apps).

    <deployment-id>             The deployment id

    <group-id>                  The group id

    <group-resource>            Path to a file containing the group's JSON
                                definition. If omitted, the definition is read
                                from stdin. For a detailed description see
                                (https://mesosphere.github.io/
                                marathon/docs/rest-api.html#post-/v2/groups).

    <instances>                 The number of instances to start

    <properties>                Must be of the format <key>=<value>. E.g.
                                cpus=2.0. If omitted, properties are read from
                                stdin.

    <task-id>                   The task id

""".encode('utf-8')
    assert_command(['dcos', 'help', 'marathon'],
                   stdout=stdout)


def test_help_node():
    stdout = """Manage DCOS nodes

Usage:
    dcos node --info
    dcos node [--json]

Options:
    -h, --help    Show this screen
    --info        Show a short description of this subcommand
    --json        Print json-formatted nodes
    --version     Show version

""".encode('utf-8')
    assert_command(['dcos', 'help', 'node'],
                   stdout=stdout)


def test_help_package():
    stdout = """Install and manage DCOS software packages

Usage:
    dcos package --config-schema
    dcos package --info
    dcos package describe [--app --options=<file> --cli] <package_name>
    dcos package install [--cli | [--app --app-id=<app_id>]]
                         [--options=<file> --yes] <package_name>
    dcos package list [--json --endpoints --app-id=<app-id> <package_name>]
    dcos package search [--json <query>]
    dcos package sources
    dcos package uninstall [--cli | [--app --app-id=<app-id> --all]]
                 <package_name>
    dcos package update [--validate]

Options:
    -h, --help         Show this screen
    --info             Show a short description of this subcommand
    --version          Show version
    --yes              Assume "yes" is the answer to all prompts and run
                       non-interactively
    --all              Apply the operation to all matching packages
    --app              Apply the operation only to the package's application
    --app-id=<app-id>  The application id
    --cli              Apply the operation only to the package's CLI
    --options=<file>   Path to a JSON file containing package installation
                       options
    --validate         Validate package content when updating sources

Configuration:
    [package]
    # Path to the local package cache.
    cache_dir = "/var/dcos/cache"

    # List of package sources, in search order.
    #
    # Three protocols are supported:
    #   - Local file
    #   - HTTPS
    #   - Git
    sources = [
      "file:///Users/me/test-registry",
      "https://my.org/registry",
      "git://github.com/mesosphere/universe.git"
    ]

""".encode('utf-8')
    assert_command(['dcos', 'help', 'package'],
                   stdout=stdout)


def test_help_service():
    stdout = """Manage DCOS services

Usage:
    dcos service --info
    dcos service [--inactive --json]
    dcos service shutdown <service-id>

Options:
    -h, --help    Show this screen

    --info        Show a short description of this subcommand

    --json        Print json-formatted services

    --inactive    Show inactive services in addition to active ones.
                  Inactive services are those that have been disconnected from
                  master, but haven't yet reached their failover timeout.

    --version     Show version

Positional Arguments:
    <service-id>  The ID for the DCOS Service

""".encode('utf-8')
    assert_command(['dcos', 'help', 'service'],
                   stdout=stdout)


def test_help_task():
    stdout = """Manage DCOS tasks

Usage:
    dcos task --info
    dcos task [--completed --json <task>]
    dcos task log [--completed --follow --lines=N] <task> [<file>]

Options:
    -h, --help    Show this screen
    --info        Show a short description of this subcommand
    --completed   Include completed tasks as well
    --follow      Output data as the file grows
    --json        Print json-formatted tasks
    --lines=N     Output the last N lines [default: 10]
    --version     Show version

Positional Arguments:

    <task>        Only match tasks whose ID matches <task>.  <task> may be
                  a substring of the ID, or a unix glob pattern.

    <file>        Output this file. [default: stdout]

""".encode('utf-8')
    assert_command(['dcos', 'help', 'task'],
                   stdout=stdout)
