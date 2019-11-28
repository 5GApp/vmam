#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# vmam -- vmam
#
#     Copyright (C) 2019 Matteo Guadrini <matteo.guadrini@hotmail.it>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
VLAN Mac-address Authentication Manager

vmam is a command line tool which allows the management and maintenance of the mac-addresses
that access the network under a specific domain and a specific VLAN, through LDAP authentication.
This is based on RFC-3579(https://tools.ietf.org/html/rfc3579#section-2.1).

    SYNOPSYS

        vmam [action] [parameter] [options]

    USAGE

        config {action}: Configuration command for vmam environment

            --new/-n {parameter}: Instruction to create a new configuration file. By specifying a path, it creates the
            file in the indicated path. The default path is /etc/vmam/vmam.cfg

            $> vmam config --new
            Create a new configuration in a standard path: /etc/vmam/vmam.cfg

            --get-cmd/-g {parameter}: Instruction to obtain the appropriate commands to configure your network
            infrastructure and radius server around the created configuration file. By specifying a path, it creates
            the file in the indicated path. The default path is /etc/vmam/vmam.cfg

            $> vmam config --get-cmd
            It takes instructions to configure its own network and radius server structure,
            from standard path: /etc/vmam/vmam.cfg

        start {action}: Automatic action for vmam environment

            --config-file/-c {parameter}: Specify a configuration file in a custom path (optional)

            $> vmam start --config-file /home/arthur/vmam.cfg
            Start automatic process based on custom path configuration file: /home/arthur/vmam.cfg

            --daemon/-d {parameter}: If specified, the automatic process run in background

            $> vmam start --daemon
            Start automatic process in background based on standard path: /etc/vmam/vmam.cfg

        mac {action}: Manual action for adding, modifying, deleting and disabling of the mac-address users

            --add/-a {parameter}: Add a specific mac-address on LDAP with specific VLAN. See also --vlan-id/-v

            $> vmam mac --add 000018ff12dd --vlan-id 110
            Add new mac-address user with VLAN 110, based on standard configuration file: /etc/vmam/vmam.cfg

            --remove/-r {parameter}: Remove a mac-address user on LDAP

            $> vmam mac --remove 000018ff12dd
            Remove mac-address user 000018ff12dd, based on standard configuration file: /etc/vmam/vmam.cfg

            --disable/-d {parameter}: Disable a mac-address user on LDAP, without removing

            $> vmam mac --disable 000018ff12dd
            Disable mac-address user 000018ff12dd, based on standard configuration file: /etc/vmam/vmam.cfg

            --force/-f {parameter}: Force add/remove/disable action

            $> vmam mac --remove 000018ff12dd --force
            Force remove mac-address user 000018ff12dd, based on standard configuration file: /etc/vmam/vmam.cfg

            $> vmam mac --add 000018ff12dd --vlan-id 111 --force
            Modify new or existing mac-address user with VLAN 111, based on standard configuration
            file: /etc/vmam/vmam.cfg

            --vlan-id/-v {parameter}: Specify a specific VLAN-id

            $> vmam mac --add 000018ff12dd --vlan-id 100
            Add new mac-address user with VLAN 100, based on standard configuration file: /etc/vmam/vmam.cfg

            --config-file/-c {parameter}: Specify a configuration file in a custom path (optional)

            $> vmam mac --remove 000018ff12dd --config-file /opt/vlan-office/office.cfg
            Remove mac-address user 000018ff12dd, based on custom configuration file: /opt/vlan-office/office.cfg

    AUTHOR

        Matteo Guadrini <matteo.guadrini@hotmail.it>

    COPYRIGHT

        (c) Matteo Guadrini. All rights reserved.
"""

# region Imports

import os
import sys
import yaml
import socket
import argparse
import platform


# endregion

# region Function for check dependencies module are installed


def check_module(module):
    """
    This function checks if a module is installed.
    :param module: The name of the module you want to check
    :return: Boolean
    ---
    >>>check_module('os')
    True
    """
    return module in sys.modules


# endregion

# region Import dependencies

import daemon
import ldap3
import winrm


# endregion

# region Functions


def read_config(path):
    """
    Open YAML configuration file
    :param path: Path of configuration file
    :return: Python object
    ---
    >>>cfg = read_config('/tmp/vmam.yml')
    >>>print(cfg)
    """
    with open('{0}'.format(path)) as file:
        return yaml.full_load(file)


def write_config(obj, path):
    """
    Write YAML configuration file
    :param obj: Python object that will be converted to YAML
    :param path: Path of configuration file
    :return: None
    ---
    >>>write_config(obj, '/tmp/vmam.yml')
    """
    with open('{0}'.format(path), 'w') as file:
        yaml.dump(obj, file)


def get_platform():
    """
    Get a platform (OS info)
    :return: Platform info dictionary
    ---
    >>>p = get_platform()
    >>>print(p)
    """
    # Create os info object
    os_info = {}
    # Check os
    if platform.system() == "Windows":
        os_info['conf_default'] = os.path.expandvars(r'%PROGRAMFILES%\vmam\vmam.yml')
        os_info['log_default'] = os.path.expandvars(r'%WINDIR%\Logs\vmam\vmam.log')
        os_info['ping_opt'] = '-n 2 -w 20000 2>&1 >NUL'
    else:
        os_info['conf_default'] = '/etc/vmam/vmam.yml'
        os_info['log_default'] = '/var/log/vmam/vmam.log'
        os_info['ping_opt'] = '-c 2 -w 20000 2>&1 >/dev/null'
    return os_info


def new_config(path=(get_platform()['conf_default'])):
    """
    Create a new vmam config file (YAML)
    :param path: Path of config file
    :return: None
    ---
    >>>new_config('/tmp/vmam.yml')
    """
    conf = {
        'LDAP': {
            'servers': ['dc1', 'dc2'],
            'domain': 'foo.bar',
            'ssl': 'true|false',
            'tls': 'true|false',
            'bind_user': 'vlan_user',
            'bind_pwd': 'secret',
            'user_base_dn': 'DC=foo,DC=bar',
            'computer_base_dn': 'DC=foo,DC=bar',
            'mac_user_base_dn': 'OU=mac-users,DC=foo,DC=bar',
            'max_computer_sync': 0,
            'time_computer_sync': '1m',
            'verify_attrib': ['memberof', 'cn'],
            'write_attrib': ['extensionattribute1', 'extensionattribute2'],
            'match': 'like|exactly',
            'add_group_type': ['user', 'computer'],
            'other_group': ['second_grp', 'third_grp']
        },
        'VMAM': {
            'mac_format': 'none|hypen|colon|dot',
            'soft_deletion': 'true|false',
            'filter_exclude': ['list1', 'list2'],
            'log': get_platform()['log_default'],
            'user_match_id': {
                'value1': 100,
                'value2': 101
            },
            'vlan_group_id': {
                100: 'group1',
                101: 'group2'
            },
            'winrm_user': 'admin',
            'winrm_pwd': 'secret'
        }
    }
    write_config(conf, path)


def check_connection(ip, port):
    """
    Test connection of remote (ip) machine on (port)
    :param ip: ip address or hostname of machine
    :param port: tcp port
    :return: Boolean
    ---
    >>>check_connection('localhost', 80)
    True
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except socket.error:
        return False


def check_config(path):
    """
    Check YAML configuration file
    :param path: Path of configuration file
    :return: Boolean
    ---
    >>>cfg = check_config('/tmp/vmam.yml')
    True
    """
    # Check exists configuration file
    assert os.path.exists(path), 'Configuration file not exists: {0}'.format(path)
    # Read the config file
    config = read_config(path)
    # Check the two principal configuration: LDAP and VMAM
    assert 'LDAP' in config, 'Key "LDAP" is required!'
    assert 'VMAM' in config, 'Key "VMAM" is required!'
    assert len(config.keys()) == 2, 'The principal keys of configuration file are two: "LDAP" and "VMAM"!'
    # Now, check mandatory fields of LDAP section
    assert ('servers' in config['LDAP'] and len(config['LDAP']['servers']) > 0), 'Required LDAP:servers: field!'
    assert ('domain' in config['LDAP'] and config['LDAP']['domain']), 'Required LDAP:domain: field!'
    assert ('bind_user' in config['LDAP'] and config['LDAP']['bind_user']), 'Required LDAP:bind_user: field!'
    assert ('bind_pwd' in config['LDAP'] and config['LDAP']['bind_pwd']), 'Required LDAP:bind_pwd: field!'
    assert ('user_base_dn' in config['LDAP'] and config['LDAP']['user_base_dn']), 'Required LDAP:user_base_dn: field!'
    assert ('computer_base_dn' in config['LDAP'] and
            config['LDAP']['computer_base_dn']), 'Required LDAP:computer_base_dn: field!'
    assert ('mac_user_base_dn' in config['LDAP'] and
            config['LDAP']['mac_user_base_dn']), 'Required LDAP:mac_user_base_dn: field!'
    assert ('verify_attrib' in config['LDAP'] and
            len(config['LDAP']['verify_attrib']) > 0), 'Required LDAP:verify_attrib: field!'
    assert ('match' in config['LDAP'] and config['LDAP']['match']), 'Required LDAP:match: field!'
    assert ('add_group_type' in config['LDAP'] and
            len(config['LDAP']['add_group_type']) > 0), 'Required LDAP:add_group_type: field!'
    # Now, check mandatory fields of VMAM section
    assert ('mac_format' in config['VMAM'] and config['VMAM']['mac_format']), 'Required VMAM:mac_format: field!'
    assert ('soft_deletion' in config['VMAM'] and
            config['VMAM']['soft_deletion']), 'Required VMAM:soft_deletion: field!'
    assert ('user_match_id' in config['VMAM'] and
            len(config['VMAM']['user_match_id'].keys()) > 0), 'Required VMAM:user_match_id: field!'
    assert ('vlan_group_id' in config['VMAM'] and
            len(config['VMAM']['vlan_group_id'].keys()) > 0), 'Required VMAM:vlan_group_id: field!'
    # Check if value of user_match_id corresponding to keys of vlan_group_id
    for k, v in config['VMAM']['user_match_id'].items():
        assert config['VMAM']['vlan_group_id'].get(v), 'Theres is no correspondence between the key {0} ' \
                                                       'in vlan_group_id and the key {1} in user_match_id!'.format(v, k)
    assert ('winrm_user' in config['VMAM'] and config['VMAM']['winrm_user']), 'Required VMAM:winrm_user: field!'
    assert ('winrm_pwd' in config['VMAM'] and config['VMAM']['winrm_pwd']), 'Required VMAM:winrm_pwd: field!'
    # Now, return ok (True)
    return True


def parse_arguments():
    """
    Function that captures the parameters and the arguments in the command line
    :return: Parser object
    ---
    >>>option = parse_arguments()
    >>>print(option.parse_args())
    """
    # Create a common parser
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('--verbose', '-v', help='enable verbosity, for debugging process.',
                               dest='verbose', action='store_true')
    # Create a principal parser
    parser_object = argparse.ArgumentParser(prog='vmam', description='VLAN Mac-address Authentication Manager',
                                            parents=[common_parser])
    # Create sub_parser "action"
    action_parser = parser_object.add_subparsers(title='action', description='valid action',
                                                 help='available actions for vmam command', dest='action')
    # config session
    config_parser = action_parser.add_parser('config', help='vmam configuration options', parents=[common_parser])
    group_config = config_parser.add_argument_group(title='configuration')
    group_config_mutually = group_config.add_mutually_exclusive_group(required=True)
    group_config_mutually.add_argument('--new', '-n', help='generate new configuration file', dest='new_conf',
                                       action='store', nargs='?', default=get_platform()['conf_default'],
                                       metavar='CONF_FILE')
    group_config_mutually.add_argument('--get-cmd', '-g', help='get information for a radius server and switch/router.',
                                       dest='get_conf', action='store_true')
    # start session
    start_parser = action_parser.add_parser('start', help='vmam automatic process options', parents=[common_parser])
    group_start = start_parser.add_argument_group(title='automatic options')
    group_start.add_argument('--config-file', '-c', help='parse configuration file', dest='conf', action='store',
                             nargs='?', default=get_platform()['conf_default'], metavar='CONF_FILE')
    group_start.add_argument('--daemon', '-d', help='start automatic process as a daemon', dest='daemon',
                             action='store_true')
    # mac session
    mac_parser = action_parser.add_parser('mac', help='vmam manual process options', parents=[common_parser])
    group_mac = mac_parser.add_argument_group(title='manual options')
    group_mac_mutually = group_mac.add_mutually_exclusive_group(required=True)
    group_mac_mutually.add_argument('--add', '-a', help='add mac-address to LDAP server', dest='add', action='store',
                                    nargs=1, metavar='MAC_ADDR')
    group_mac_mutually.add_argument('--remove', '-r', help='remove mac-address to LDAP server', dest='remove',
                                    action='store', nargs=1, metavar='MAC_ADDR')
    group_mac_mutually.add_argument('--disable', '-d', help='disable mac-address to LDAP server', dest='disable',
                                    action='store', nargs=1, metavar='MAC_ADDR')
    group_mac.add_argument('--config-file', '-c', help='parse configuration file', dest='conf', action='store',
                           nargs='?', default=get_platform()['conf_default'], metavar='CONF_FILE')
    group_mac.add_argument('--force', '-f', help='force action', dest='force', action='store_true')
    group_mac.add_argument('--vlan-id', '-i', help='vlan-id number', dest='vlanid', action='store',
                           nargs=1, metavar='VLAN_ID', required=True)
    # Return parser object
    return parser_object


# endregion


# region Start process

if __name__ == '__main__':

    # Check import dependencies
    if not check_module('daemon'):
        print('Install daemon module: pip3 install python-daemon')
        exit(1)

    if not check_module('ldap3'):
        print('Install ldap3 module: pip3 install ldap3')
        exit(1)

    if not check_module('winrm'):
        print('Install winrm module: pip3 install pywinrm')
        exit(1)

    option = parse_arguments()
    args = option.parse_args()

# endregion
