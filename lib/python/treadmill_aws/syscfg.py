"""Configure treadmill environment variables for sysctl.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import click
import requests
from six.moves import http_client
import yaml


_USERDATA_URL = 'http://169.254.169.254/latest/user-data'


def _load_userdata(url):
    """Reads user data as dictionary."""
    resp = requests.get(url)
    if resp.status_code == http_client.NOT_FOUND:
        return {}

    return yaml.load(resp.text)


def _write_env_file(conf_file, userdata, prefixes=()):
    """Read userdata and print environment variables for each."""
    for key, value in userdata.items():
        for prefix in prefixes:
            if key.startswith(prefix):
                conf_file.write('{}={}\n'.format(key.upper(), value))


@click.group()
@click.option('--userdata', help='Userdata url',
              default=_USERDATA_URL)
@click.pass_context
def syscfg(ctx, userdata):
    """Configures environment for Treadmill systemd services."""
    ctx.obj['USERDATA_URL'] = userdata


@syscfg.command()
@click.option('--envfile',
              required=True,
              type=click.File(mode='w'),
              help='Environent file location.')
@click.option('--prefix',
              multiple=True,
              default=['treadmill_'],
              help='Environent variable location.')
@click.pass_context
def write(ctx, envfile, prefix):
    """Configure environment vars."""
    url = ctx.obj['USERDATA_URL']
    userdata = _load_userdata(url)
    _write_env_file(envfile, userdata, prefix)


def run():
    """Console entry point."""
    # Pylint complains about click signature magic.
    #
    # [E1123(unexpected-keyword-arg), run] \
    #     Unexpected keyword argument 'obj' in function call
    #
    # [E1120(no-value-for-parameter), run] \
    #     No value for argument 'ctx', 'userdata' in function call
    #
    # pylint: disable=E1120,E1123
    syscfg(obj={})
