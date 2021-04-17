import paramiko
from time import sleep
import re
from tabulate import tabulate
import pandas as pd


class G8PSX:

    def __init__(self, host, port, username, password):
        # All variables are self explained...
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect_ssh(self, command_syntax):

        # Method to connect to a host through SSH, run commands and return the shell output.
        # It can run a single command if the command_syntax is a string, or a sequence of commands if It is a list.

        output = str

        try:
            if self.ssh_client.get_transport().is_active():
                print('Utilizando conexão já estabelecida...\n')
        except AttributeError:
            try:
                print('Estabelecendo conexão SSH... host: ' + self.host + '\n')
                self.ssh_client.connect(hostname=self.host, port=self.port, username=self.username,
                                        password=self.password,
                                        look_for_keys=False, allow_agent=False)
            except:
                print('Não foi possível estabelecer conexão SSH com o node ' + self.host)
                raise ValueError

        shell = self.ssh_client.invoke_shell()
        sleep(1)
        shell.send('enable\n')
        sleep(1)
        shell.send('config\n')
        sleep(1)
        if isinstance(command_syntax, list):
            for command in command_syntax:
                shell.send(command + '\n')
                # sleep(1)
            output = shell.recv(100000).decode('utf-8')
        elif isinstance(command_syntax, str):
            shell.send(command_syntax + '\n')
            sleep(1)
            output = shell.recv(100000).decode('utf-8')

        return output

    def output_to_list(self, command, re_matchstr=r'^  \d+'):
        output_raw = self.connect_ssh(command).splitlines()
        output_list = []
        index = 0
        for line in output_raw:
            if re.match(re_matchstr, line):
                index = index + 1
                line = line.split()
                line.insert(0, index)
                output_list.append(line)

        return output_list

    def get_onu_info(self, command="show ont info all", printthis=False):
        # Get the registered ONUs at the OLT, and creates a dic for each entry found. The entrys are stored on a list
        # (onulist). Each entry (dic) contains the following ONU attributes as keys: Option, port, ONU_ID PON_SN,
        # CTRL_FLAG, RUN_STATE, Config_State, Match_state
        onulist_raw = self.output_to_list(command, re_matchstr=r'  0/0')
        onudic = []
        index = 0

        for line in onulist_raw:
            index = index + 1
            onudic.append({'OPTION': index,
                           'PORT': line[2],
                           'ONU_ID': line[3],
                           'PON_SN': line[4],
                           'CTRL_FLAG)': line[5],
                           'RUN STATE': line[6],
                           'CONFIG_STATE': line[7],
                           'MATCH STATE': line[8]
                           })

        if not printthis:
            return onudic
        else:
            df = pd.DataFrame(onudic)
            header = onudic[0].keys()
            print(tabulate(df, header, showindex=False))
            return onudic

    def get_onu_summary_cfg(self, port='8', onu_id='110', sn='xxxx00000000'):
        # Search for a specific ONU, identified by port and onu_id, then returns a dictionary (onu_config) with
        # lineprofile-id, srvprofile-id and service-port as keys. the first two will have single string values as pair,
        # service-port will have another dictionary as value, containing service-port the attributes:svlan, cvlan
        # and tag-action
        command = ['show ont info all',
                   'show current-config section gpon',
                   'show ont-lineprofile gpon all',
                   'show srv-lineprofile gpon all',
                   'show service-port all',




                   ]
        pon_att_list = self.get_onu_info()
        output_raw = self.output_to_list(command, re_matchstr=r'  0/0')

    def clear_onu_config(self, pon_sn):
        # Search and destroy ONU configuration
        print('iniciando limpeza de configuração da ONU: ' + pon_sn)
        onulist = self.get_onu_info()
        target_port = '0'
        target_id = '0'
        for line in onulist:
            if line[2] == pon_sn:
                target_port = line[0]
                target_id = line[1]

        if target_port and target_id == '0':
            print('Nenhuma configuração prévia encontrada')

        else:
            print('Apagando configuração prévia...')
            command_list = ['interface gpon 0/0', 'ont del ' + target_port + ' ' + target_id, 'exit']
            self.connect_ssh(command_list)

    def set_line_profile(self, vlan_id):
        line_profile_id = 110
        line_profile_name = 'py_' + vlan_id
        id_list = self.output_to_list('show ont-lineprofile gpon all', '  ')

        for line in id_list:
            if line[2] == line_profile_name:
                line_profile_id = line[1]
                print('Utilizando line-profile já existente... ID: ' + line_profile_id)
                return line_profile_id

        restart = True
        while restart:
            restart = False
            for line in id_list:
                if line[1] == str(line_profile_id):
                    line_profile_id = line_profile_id + 1
                    restart = True

        command_list = [
            'ont-lineprofile gpon profile-id ' + str(line_profile_id) + ' profile-name ' + line_profile_name,
            'tcont 1 dba-profile-id 1',
            'gem add 1 tcont 1 encrypt off',
            'gem mapping 1 1 vlan ' + vlan_id,
            'commit'
            'exit'
        ]
        self.connect_ssh(command_list)
        return line_profile_id

    def set_srv_profile(self, vlan_id, type_name):
        srv_profile_id = 110

        if type_name == 'sfu_trunk' or 'sfu_access':
            srv_profile_name = 'py_' + type_name + '_' + vlan_id
        else:
            srv_profile_name = "py_HGU_default"

        id_list = self.output_to_list('show ont-srvprofile gpon all', '  ')

        for line in id_list:
            if line[2] == srv_profile_name:
                line_profile_id = line[1]
                print('Utilizando srv-profile já existente... ID: ' + line_profile_id)
                return srv_profile_id

        restart = True
        while restart:
            restart = False
            for line in id_list:
                if line[1] == str(srv_profile_id):
                    srv_profile_id = srv_profile_id + 1
                    restart = True

        if type_name == 'sfu_trunk':
            command_list = [
                'ont-srvprofile gpon profile-id ' + str(srv_profile_id) + ' profile-name ' + srv_profile_name,
                'port vlan eth 1 translation ' + vlan_id + ' user-vlan ' + vlan_id,
                'commit'
                'exit'
            ]
        elif type_name == 'sfu_access':
            command_list = [
                'ont-srvprofile gpon profile-id ' + str(srv_profile_id) + ' profile-name ' + srv_profile_name,
                'port vlan eth 1 translation ' + vlan_id + ' user-vlan ' + vlan_id,
                'port native-vlan eth 1 ' + vlan_id,
                'commit',
                'exit'
            ]

        elif type_name == 'hgu':
            command_list = [
                'ont-srvprofile gpon profile-id ' + str(srv_profile_id) + ' profile-name ' + srv_profile_id,
                'port vlan eth 1 transparent',
                'port vlan eth 2 transparent',
                'port vlan eth 3 transparent',
                'port vlan eth 4 transparent',
                'commit'
                'exit'
            ]

        self.connect_ssh(command_list)
        return srv_profile_id


teste = G8PSX('172.31.0.29', '22', 'admin', 'admin')
teste.get_onu_info(printthis=True)
