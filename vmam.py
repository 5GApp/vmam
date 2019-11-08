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
Welcome to doc of vmam: VLAN Mac-address Authentication Manager

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