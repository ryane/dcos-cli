import collections
import contextlib
import json
import os
import pty
import subprocess
import sys
import time

import requests
import six
from dcos import util

import mock
from six.moves import urllib


def exec_command(cmd, env=None, stdin=None):
    """Execute CLI command

    :param cmd: Program and arguments
    :type cmd: [str]
    :param env: Environment variables
    :type env: dict
    :param stdin: File to use for stdin
    :type stdin: file
    :returns: A tuple with the returncode, stdout and stderr
    :rtype: (int, bytes, bytes)
    """

    print('CMD: {!r}'.format(cmd))

    process = subprocess.Popen(
        cmd,
        stdin=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env)

    # This is needed to get rid of '\r' from Windows's lines endings.
    stdout, stderr = [std_stream.replace(b'\r', b'')
                      for std_stream in process.communicate()]

    # We should always print the stdout and stderr
    print('STDOUT: {}'.format(_truncate(stdout.decode('utf-8'))))
    print('STDERR: {}'.format(_truncate(stderr.decode('utf-8'))))

    return (process.returncode, stdout, stderr)


def _truncate(s, length=8000):
    if len(s) > length:
        return s[:length-3] + '...'
    else:
        return s


def assert_command(
        cmd,
        returncode=0,
        stdout=b'',
        stderr=b'',
        env=None,
        stdin=None):
    """Execute CLI command and assert expected behavior.

    :param cmd: Program and arguments
    :type cmd: list of str
    :param returncode: Expected return code
    :type returncode: int
    :param stdout: Expected stdout
    :type stdout: str
    :param stderr: Expected stderr
    :type stderr: str
    :param env: Environment variables
    :type env: dict of str to str
    :param stdin: File to use for stdin
    :type stdin: file
    :rtype: None
    """

    returncode_, stdout_, stderr_ = exec_command(cmd, env, stdin)

    assert returncode_ == returncode
    assert stdout_ == stdout
    assert stderr_ == stderr


def exec_mock(main, args):
    """Call a main function with sys.args mocked, and capture
    stdout/stderr

    :param main: main function to call
    :type main: function
    :param args: sys.args to mock, excluding the initial 'dcos'
    :type args: [str]
    :returns: (returncode, stdout, stderr)
    :rtype: (int, bytes, bytes)
    """

    print('MOCK ARGS: {}'.format(' '.join(args)))

    with mock_args(args) as (stdout, stderr):
        returncode = main()

    stdout_val = six.b(stdout.getvalue())
    stderr_val = six.b(stderr.getvalue())

    print('STDOUT: {}'.format(stdout_val))
    print('STDERR: {}'.format(stderr_val))

    return (returncode, stdout_val, stderr_val)


def assert_mock(main,
                args,
                returncode=0,
                stdout=b'',
                stderr=b''):
    """Mock and call a main function, and assert expected behavior.

    :param main: main function to call
    :type main: function
    :param args: sys.args to mock, excluding the initial 'dcos'
    :type args: [str]
    :type returncode: int
    :param stdout: Expected stdout
    :type stdout: str
    :param stderr: Expected stderr
    :type stderr: str
    :rtype: None
    """

    returncode_, stdout_, stderr_ = exec_mock(main, args)

    assert returncode_ == returncode
    assert stdout_ == stdout
    assert stderr_ == stderr


def mock_called_some_args(mock, *args, **kwargs):
    """Convience method for some mock assertions.  Returns True if the
    arguments to one of the calls of `mock` contains `args` and
    `kwargs`.

    :param mock: the mock to check
    :type mock: mock.Mock
    :returns: True if the arguments to one of the calls for `mock`
    contains `args` and `kwargs`.
    :rtype: bool
    """

    for call in mock.call_args_list:
        call_args, call_kwargs = call

        if any(arg not in call_args for arg in args):
            continue

        if any(k not in call_kwargs or call_kwargs[k] != v
               for k, v in kwargs.items()):
            continue

        return True

    return False


def watch_deployment(deployment_id, count):
    """ Wait for a deployment to complete.

    :param deployment_id: deployment id
    :type deployment_id: str
    :param count: max number of seconds to wait
    :type count: int
    :rtype: None
    """

    returncode, stdout, stderr = exec_command(
        ['dcos', 'marathon', 'deployment', 'watch',
            '--max-count={}'.format(count), deployment_id])

    assert returncode == 0
    assert stderr == b''


def watch_all_deployments(count=300):
    """ Wait for all deployments to complete.

    :param count: max number of seconds to wait
    :type count: int
    :rtype: None
    """

    deps = list_deployments()
    for dep in deps:
        watch_deployment(dep['id'], count)


def add_app(app_path, deploy=False):
    """ Add an app, and wait for it to deploy

    :param app_path: path to app's json definition
    :type app_path: str
    :rtype: None
    """

    assert_command(['dcos', 'marathon', 'app', 'add', app_path])

    if deploy:
        watch_all_deployments()


def remove_app(app_id):
    """ Remove an app

    :param app_id: id of app to remove
    :type app_id: str
    :rtype: None
    """

    assert_command(['dcos', 'marathon', 'app', 'remove', app_id])


def package_install(package, deploy=False, args=[]):
    """ Calls `dcos package install`

    :param package: name of the package to install
    :type package: str
    :param deploy: whether or not to wait for the deploy
    :type deploy: bool
    :param args: extra CLI args
    :type args: [str]
    :rtype: None
    """

    returncode, stdout, stderr = exec_command(
        ['dcos', 'package', 'install', '--yes', package] + args)

    assert returncode == 0
    assert stderr == b''

    if deploy:
        watch_all_deployments()


def package_uninstall(package, args=[]):
    """ Calls `dcos package uninstall`

    :param package: name of the package to uninstall
    :type package: str
    :param args: extra CLI args
    :type args: [str]
    :rtype: None
    """

    assert_command(['dcos', 'package', 'uninstall', package] + args)


def get_services(expected_count=None, args=[]):
    """Get services

    :param expected_count: assert exactly this number of services are
        running
    :type expected_count: int | None
    :param args: cli arguments
    :type args: [str]
    :returns: services
    :rtype: [dict]
    """

    returncode, stdout, stderr = exec_command(
        ['dcos', 'service', '--json'] + args)

    assert returncode == 0
    assert stderr == b''

    services = json.loads(stdout.decode('utf-8'))
    assert isinstance(services, collections.Sequence)
    if expected_count is not None:
        assert len(services) == expected_count

    return services


def list_deployments(expected_count=None, app_id=None):
    """Get all active deployments.

    :param expected_count: assert that number of active deployments
    equals `expected_count`
    :type expected_count: int
    :param app_id: only get deployments for this app
    :type app_id: str
    :returns: active deployments
    :rtype: [dict]
    """

    cmd = ['dcos', 'marathon', 'deployment', 'list', '--json']
    if app_id is not None:
        cmd.append(app_id)

    returncode, stdout, stderr = exec_command(cmd)

    result = json.loads(stdout.decode('utf-8'))

    assert returncode == 0
    if expected_count is not None:
        assert len(result) == expected_count
    assert stderr == b''

    return result


def show_app(app_id, version=None):
    """Show details of a Marathon application.

    :param app_id: The id for the application
    :type app_id: str
    :param version: The version, either absolute (date-time) or relative
    :type version: str
    :returns: The requested Marathon application
    :rtype: dict
    """

    if version is None:
        cmd = ['dcos', 'marathon', 'app', 'show', app_id]
    else:
        cmd = ['dcos', 'marathon', 'app', 'show',
               '--app-version={}'.format(version), app_id]

    returncode, stdout, stderr = exec_command(cmd)

    assert returncode == 0
    assert stderr == b''

    result = json.loads(stdout.decode('utf-8'))
    assert isinstance(result, dict)
    assert result['id'] == '/' + app_id

    return result


def service_shutdown(service_id):
    """Shuts down a service using the command line program

    :param service_id: the id of the service
    :type: service_id: str
    :rtype: None
    """

    assert_command(['dcos', 'service', 'shutdown', service_id])


def delete_zk_nodes():
    """Delete Zookeeper nodes that were created during the tests

    :rtype: None
    """

    base_url = os.environ['EXHIBITOR_URL']
    base_path = 'exhibitor/v1/explorer/znode/{}'

    for znode in ['universe', 'cassandra-mesos', 'chronos']:
        znode_url = urllib.parse.urljoin(
            base_url,
            base_path.format(znode))

        requests.delete(znode_url)


def assert_lines(cmd, num_lines):
    """ Assert stdout contains the expected number of lines

    :param cmd: program and arguments
    :type cmd: [str]
    :param num_lines: expected number of lines for stdout
    :type num_lines: int
    :rtype: None
    """

    returncode, stdout, stderr = exec_command(cmd)

    assert returncode == 0
    assert stderr == b''
    assert len(stdout.decode('utf-8').split('\n')) - 1 == num_lines


def file_bytes(path):
    """ Read all bytes from a file

    :param path: path to file
    :type path: str
    :rtype: bytes
    :returns: bytes from the file
    """

    with open(path) as f:
        return six.b(f.read())


@contextlib.contextmanager
def app(path, app_id, deploy=False):
    """Context manager that deploys an app on entrance, and removes it on
    exit.

    :param path: path to app's json definition:
    :type path: str
    :param app_id: app id
    :type app_id: str
    :rtype: None
    """

    add_app(path, deploy)
    try:
        yield
    finally:
        remove_app(app_id)


@contextlib.contextmanager
def package(package_name, deploy=False, args=[]):
    """Context manager that deploys an app on entrance, and removes it on
    exit.

    :param package_name: package name
    :type package_name: str
    :param deploy: If True, block on the deploy
    :type deploy: bool
    :rtype: None
    """

    package_install(package_name, deploy, args)
    try:
        yield
    finally:
        package_uninstall(package_name)


@contextlib.contextmanager
def mock_args(args):
    """ Context manager that mocks sys.args and captures stdout/stderr

    :param args: sys.args values to mock
    :type args: [str]
    :rtype: None
    """
    with mock.patch('sys.argv', [util.which('dcos')] + args):
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = six.StringIO(), six.StringIO()
        try:
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = stdout, stderr


def ssh_output(cmd):
    """ Runs an SSH command and returns the stdout/stderr.

    :param cmd: command to run
    :type cmd: str
    :rtype: (str, str)
    """

    # ssh must run with stdin attached to a tty
    master, slave = pty.openpty()
    proc = subprocess.Popen(cmd,
                            stdin=slave,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            preexec_fn=os.setsid,
                            close_fds=True,
                            shell=True)
    os.close(slave)

    # wait for the ssh connection
    time.sleep(8)

    # kill the whole process group
    os.killpg(os.getpgid(proc.pid), 15)

    os.close(master)
    stdout, stderr = proc.communicate()

    print('SSH STDOUT: {}'.format(stdout.decode('utf-8')))
    print('SSH STDERR: {}'.format(stderr.decode('utf-8')))

    return stdout, stderr
