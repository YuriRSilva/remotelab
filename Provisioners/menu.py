from g8psx import G8PSX
import re
from tabulate import tabulate

file = 'cenarios'
start_index = 1
configlist = [line.rsplit() for line in open(file, 'r', encoding='UTF-8').read().splitlines() if
              re.match(r'^sfu|^hgu|^pppoe|^dhcp|^static', line)]

olt_lab = G8PSX('172.31.0.29', '22', 'admin', 'admin')


def index_inserter(line):
    global start_index
    line.insert(0, str(start_index))
    start_index += 1
    return line


def mainmenu():
    tab_style = 'pretty'

    # Print and select a ONU.
    print('Selecione a ONU: ')
    olt_lab.get_onus_info(printthis=True)
    option = input('\n Opção: ')
    pon_sn = olt_lab.get_onus_info(chosen_onu=option)

    # Split and groups the configlist by the config type, then insert a index for the user to choose
    sfu_cfgs = [index_inserter(line) for line in configlist if line[0] == 'sfu']
    hgu_cfgs = [index_inserter(line) for line in configlist if line[0] == 'hgu']
    pppoe_cfgs = [index_inserter(line) for line in configlist if line[0] == 'pppoe']
    dhcp_cfgs = [index_inserter(line) for line in configlist if line[0] == 'dhcp']
    static_cfgs = [index_inserter(line) for line in configlist if line[0] == 'static']

    print('\nSelecione a opção de profile: \n')
    print('\n', tabulate(sfu_cfgs, ['OPÇÃO', 'TIPO', 'VLAN_ID', 'LAN_MODE'], tablefmt=tab_style))
    print('\n', tabulate(hgu_cfgs, ['OPÇÃO', 'TIPO', 'VLAN_ID'], tablefmt=tab_style))
    print('\n', tabulate(pppoe_cfgs, ['OPÇÃO', 'TIPO', 'VLAN_ID', 'USERNAME', 'PASSWORD'], tablefmt=tab_style))
    print('\n', tabulate(dhcp_cfgs, ['OPÇÃO', 'TIPO', 'VLAN_ID'], tablefmt=tab_style))
    print('\n', tabulate(static_cfgs, ['OPÇÃO', 'TIPO', 'VLAN_ID', 'IP_ADDRESS', 'NETMASK', 'IP_GATEWAY', 'DNS_PRIMARY',
                                       'DNS_SECONDARY'], tablefmt=tab_style))
    option = input('\nOPÇÃO: ')

    # Extract the line with the configuration choosed by user, then creates a dictionary :param cfg_list: containing all
    # parameters for the cgf_onu method of g8psx class.

    indexed_cfgs = sfu_cfgs + hgu_cfgs + pppoe_cfgs + dhcp_cfgs + static_cfgs
    cfg_list = indexed_cfgs[int(option) - 1]
    cfg_dict = {}

    if cfg_list[1] == 'sfu':
        cfg_dict = {'config_type': cfg_list[1], 'vlan_id': cfg_list[2], 'sfu_lan_type': cfg_list[3]}
    elif cfg_list[1] == 'hgu':
        cfg_dict = {'config_type': cfg_list[1], 'vlan_id': cfg_list[2]}
    elif cfg_list[1] == 'pppoe':
        cfg_dict = {'config_type': cfg_list[1], 'vlan_id': cfg_list[2], 'pppoe_username': cfg_list[3], 'pppoe_password': cfg_list[4]}
    elif cfg_list[1] == 'dhcp':
        cfg_dict = {'config_type': cfg_list[1], 'vlan_id': cfg_list[2]}
    elif cfg_list[1] == 'static':
        cfg_dict = {'config_type': cfg_list[1], 'vlan_id': cfg_list[2], 'wan_ip_addr': cfg_list[3], 'wan_netmask': cfg_list[4], 'wan_gateway': cfg_list[5], 'dns_1': cfg_list[6], 'dns_2': cfg_list[7]}

    olt_lab.cfg_onu(pon_sn, **cfg_dict)


mainmenu()
