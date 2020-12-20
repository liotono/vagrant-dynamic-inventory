#!/usr/bin/env python3

"""
This script was developed based on the information found in
https://docs.ansible.com/ansible/2.5/dev_guide/developing_inventory.html
"""

import vagrant
import argparse
import json

"""Host types defined in Vagrantfile"""
hosts_types = ['deployment', 'lb', 'controller', 'compute', 'network', 'ceph', 
        'cinder', 'swift', 'logging', 'nfs']

"""
This function will return a sub-list of hosts. All hosts whose name
contains the string name will be added to such sublist.
Arguments:
    hosts: A list returned by the function Vagrant.status()
    name: The type of host (ceph, swift, compute, etc.)
"""
def get_hosts_sublist(hosts, name):
    hosts_sublist = []

    for host in hosts:
        if host.name.find(name) != -1:
            hosts_sublist.append(host)

    return hosts_sublist

"""
This function will create an ansible group from the host list
provided.
Arguments:
    host_list: List of hosts returned by Vagrant.status()
    inventory: Ansible inventory being created
    group_name: Group to be created
"""
def create_group(host_list, inventory, group_name):

    inventory.update({ group_name : { "hosts": [] } })

    for host in host_list:
        inventory[group_name]['hosts'].append(host.name)

    return inventory

def create_dynamic_inventory(inventory):

    """ Get the list of Vagrant instances """
    v = vagrant.Vagrant()
    hosts_vagrant_list = v.status()

    """
    Based on every host type defined in hosts_types, we collect
    hosts from the list of instances returned by Vagrant and create an
    ansible group
    """
    for host_type in hosts_types:
        host_list = get_hosts_sublist(hosts_vagrant_list, host_type)
        if len(host_list) > 0:
            inventory = create_group(host_list, inventory,
                    host_type + "_nodes" )

    """ Now we add every host to the all group """
    inventory = create_group(hosts_vagrant_list, inventory, "all")

    return inventory

def dynamic_inventory(args):
    """ Create an empty inventory """
    inventory = json.loads('{ "_meta": { "hostvars": {} } }')

    """ When the script is invoked with the option --list """
    if args.list:
        inventory = create_dynamic_inventory(inventory)

    """ Print the inventory to the standar output """
    print(json.dumps(inventory, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--list',
        help='Output to stdout a JSON-encoded dictionary containing all of the groups',
        action="store_true")
    parser.add_argument('--host',
        help='Print either an empty JSON hash/dictionary, or a hash/dictionary of variables',
        type=str)
    args = parser.parse_args()
    
    dynamic_inventory(args)
