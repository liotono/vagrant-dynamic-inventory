#!/usr/bin/env python3

"""
This script was developed based on the information found in
https://docs.ansible.com/ansible/2.5/dev_guide/developing_inventory.html
"""

import vagrant
import argparse
import json

"""
Global variables that need to be modified based on the enviroment
"""
ip_brmgmt = "172.29.236."
ip_brvxlan = "172.29.240."
ip_brstorage = "172.29.244."
ip_public = "192.168.15."
ip_block_start = {"deployment": 10, "lb": 20, "controller": 30,
        "compute": 40, "network": 50, "ceph": 60, "cinder": 70,
        "swift": 80, "logging": 90, "nfs": 100}

"""Host types defined in Vagrantfile"""
hosts_types = ['deployment', 'lb', 'controller', 'compute', 'network', 'ceph', 
        'cinder', 'swift', 'logging', 'nfs']

"""
This function will return a sublist of the list hosts. All the hosts whose name
contains the string name will be added to such sublist and remove from hosts.
hosts: a list returned by the function Vagrant.status()
name: the type of host (ceph, swift, compute, etc.)
"""
def get_hosts_sublist(hosts, name):
    hosts_sublist = []

    for i in range(0,len(hosts)-1):
        if hosts[i].name.find(name) != -1:
            hosts_sublist.append(hosts[i])

    return hosts_sublist


"""v = vagrant.Vagrant()
hosts_list = v.status()
ceph_list = get_hosts_sublist(hosts_list, 'ceph')
"""

"""
_inventory.update({ "ceph_nodes": {} })
_inventory['_meta']['hostvars'].update({ "ceph00": {} })
_inventory['_meta']['hostvars']["ceph00"].update({ "var2": 4 })
_inventory['_meta']['hostvars'].update({ "ceph01": {} })
"""

def create_hostvars(host_list, host_type, inventory):

    ip_start = ip_block_start[host_type]

    for host in host_list:
        inventory['_meta']['hostvars'].update({ host.name: {} })
        inventory['_meta']['hostvars'][host.name].update( { "ip_brmgmt": ip_brmgmt + str(ip_start) } )
        inventory['_meta']['hostvars'][host.name].update( { "ip_brvxlan": ip_brvxlan + str(ip_start) } )
        inventory['_meta']['hostvars'][host.name].update( { "ip_brstorage": ip_brstorage + str(ip_start) } )
        inventory['_meta']['hostvars'][host.name].update( { "ip_public": ip_public + str(ip_start) } )
        inventory['_meta']['hostvars'][host.name].update( { "ansible_host": host.name } )
        ip_start += 1

    return inventory

def create_group(host_list, host_type, inventory):

    group_name = host_type + '_nodes'

    inventory.update({ group_name : { "hosts": [] } })

    for host in host_list:
        inventory[group_name]['hosts'].append(host.name)

    return inventory

def create_static_groups(inventory):

    static_groups = json.loads('{ "infrastructure_nodes": {} }' )
    static_groups['infrastructure_nodes'].update({ "children": [ ] })
    
    for i in range(1, len(hosts_types)):
        static_groups['infrastructure_nodes']['children'].append( hosts_types[i] + '_nodes' )

    inventory.update( static_groups )

    return inventory

def create_dynamic_inventory(inventory):

    """Get the list of Vagramt instances"""
    v = vagrant.Vagrant()
    hosts_vagrant_list = v.status()

    """Add the hostvars object to the inventory"""
    inventory['_meta'].update({ "hostvars": {} })

    for host_type in hosts_types:
        host_list = get_hosts_sublist(hosts_vagrant_list, host_type)
        if len(host_list) > 0:
            inventory = create_hostvars(host_list, host_type, inventory)
            inventory = create_group(host_list, host_type, inventory)

    """Create static groups"""
    inventory = create_static_groups(inventory)

    return inventory

def dynamic_inventory(args):

    inventory = json.loads('{ "_meta" : {} }')

    if args.list:
        inventory = create_dynamic_inventory(inventory)

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
