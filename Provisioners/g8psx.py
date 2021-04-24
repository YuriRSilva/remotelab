import paramiko
from time import sleep
import re
from tabulate import tabulate
import pandas as pd
from paramiko_expect import SSHClientInteraction

display_ssh = False  # Display the SSH inputs and outputs


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
        max_attempts = 4
        attempt = 1
        while attempt <= 4:
            if self.ssh_client.get_transport() is None:
                try:
                    print('Estabelecendo conexão SSH com o host: ' + self.host)
                    self.ssh_client.connect(hostname=self.host, port=self.port, username=self.username,
                                            password=self.password,
                                            look_for_keys=False, allow_agent=False)
                except ValueError:
                    print("Não foi possível abrir a sessão SSH")
                    attempt = attempt + 1
                    continue
            else:
                try:
                    with SSHClientInteraction(self.ssh_client, timeout=5, display=display) as interact:
                        sleep(1)
                        interact.send('enable\n')
                        interact.expect(r'\w+#\s+')
                        interact.send('config\n')
                        prompt = r'\w+\([a-z-\d/]+\)#\s+'
                        interact.expect(prompt)
                        interact.send('vty output show-all\n')
                        interact.expect(prompt)

                        if isinstance(command_syntax, list):
                            for command in command_syntax:
                                interact.send(command + '\n')
                                interact.expect(prompt)

                        elif isinstance(command_syntax, str):
                            interact.send(command_syntax + '\n')
                            interact.expect(prompt)

                        output = str(interact.current_output_clean)
                        return output
                except ValueError:
                    print("Não foi possível executar comandos na sessão SSH")
                    print("Tentativa " + str(attempt) + "/" + str(max_attempts))
                    attempt = attempt + 1
                    continue

        print('Tentativas esgotadas para conexão SSH')

    def output_to_list(self, command, re_matchstr=r'^  \d+'):
        """
        Connects on the host and runs a command, then create a list for each line that matchs re_matchstr
        """
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

    def get_onus_info(self, pon_sn='all', printthis=False):
        # Get the registered and unregistered ONUs at the OLT, and creates a dic for each entry found. The entrys are
        # stored on a list (onulist). Each entry (dic) contains the following ONU attributes as keys: Option, port,
        # ONU_ID PON_SN, RUN_STATE, Config_State, Match_state

        reg_onulist_raw = self.output_to_list('show ont info all', re_matchstr=r'^  \d+')
        unreg_onulist_raw = self.output_to_list('show ont autofind all brief', re_matchstr=r'^  \d+')
        onus = []
        index = 0
        if pon_sn == 'all':
            for line in reg_onulist_raw:
                index = index + 1
                onus.append({'OPTION': index,
                             'PORT': line[2],
                             'ONU_ID': line[3],
                             'PON_SN': line[4],
                             'RUN STATE': line[6],
                             'CONFIG_STATE': line[7],
                             'MATCH STATE': line[8]
                             })
            for line in unreg_onulist_raw:
                index = index + 1
                line[2] = re.sub(r'^\d/\d/', '', line[2])
                onus.append({'OPTION': index,
                             'PORT': line[2],
                             'ONU_ID': '-',
                             'PON_SN': line[3],
                             'RUN STATE': 'UNAUTHORIZED',
                             'CONFIG_STATE': 'UNAUTHORIZED',
                             'MATCH STATE': '-'
                             })
        else:
            if len(pon_sn) == 12:
                for line in reg_onulist_raw:
                    if line[4] == pon_sn:
                        index = index + 1
                        onus.append({'OPTION': index,
                                     'PORT': line[2],
                                     'ONU_ID': line[3],
                                     'PON_SN': line[4],
                                     'RUN STATE': line[6],
                                     'CONFIG_STATE': line[7],
                                     'MATCH STATE': line[8]
                                     })
                        break
                for line in unreg_onulist_raw:
                    if line[3] == pon_sn:
                        index = index + 1
                        line[2] = re.sub(r'^\d/\d/', '', line[2])
                        onus.append({'OPTION': index,
                                     'PORT': line[2],
                                     'ONU_ID': '-',
                                     'PON_SN': line[3],
                                     'RUN STATE': 'UNAUTHORIZED',
                                     'CONFIG_STATE': 'UNAUTHORIZED',
                                     'MATCH STATE': '-'
                                     })
                        break

        if printthis:
            df = pd.DataFrame(onus)
            header = onus[0].keys()
            print(tabulate(df, header, showindex=False))
            return onus
        else:
            return onus

    def clear_onu_config(self, pon_sn):
        # Search and destroy ONU configuration

        print('iniciando limpeza de configuração da ONU: ' + pon_sn)
        target_port = '0'
        target_id = '0'
        onulist = self.get_onus_info()

        for line in onulist:
            if line['PON_SN'] == pon_sn:
                target_port = line['PORT']
                target_id = line['ONU_ID']

        if target_port and target_id == '0':
            print('Nenhuma configuração prévia encontrada')
        else:
            print('Apagando configuração prévia...')
            command_list = ['interface gpon 0/0', 'ont del ' + target_port + ' ' + target_id, 'exit']
            self.connect_ssh(command_list)

    def cfg_line_profile(self, vlan_id):
        """
        This function is to inform what line profile ID it needs to be used that match the vlan_id informed. At first
        it searchs for a profile named py_ + vlan ID, then returns his ID value. If there is no match, It creates a line
        profile ID with the name py_ + vlan_id then returns the profile ID value
        :param self:
        :param vlan_id: Vlan that the gemport will be associated
        :return: Return the line profile ID value that corresponds to the vlan_id
        """

        line_profile_id = 110
        line_profile_name = 'py_' + vlan_id
        id_list = self.output_to_list('show ont-lineprofile gpon all', '  ')

        for line in id_list:  # Verify if the profile already exists and returns his ID
            if line[2] == line_profile_name:
                line_profile_id = line[1]
                print('Utilizando line-profile já existente... ID: ' + line_profile_id)
                return line_profile_id

        for line in id_list:  # Search for a unused ID value
            if line[1] == str(line_profile_id):
                line_profile_id = line_profile_id + 1

        command_list = [
            'ont-lineprofile gpon profile-id ' + str(line_profile_id) + ' profile-name ' + line_profile_name,
            'tcont 1 dba-profile-id 1',
            'gem add 1 tcont 1 encrypt off',
            'gem mapping 1 1 vlan ' + vlan_id,
            'commit',
            'exit'
        ]
        self.connect_ssh(command_list)
        return line_profile_id

    def cfg_srv_profile(self, vlan_id, type_name):
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

        for line in id_list:
            if line[1] == str(srv_profile_id):
                srv_profile_id = srv_profile_id + 1

        if type_name == 'sfu_trunk':
            command_list = [
                'ont-srvprofile gpon profile-id ' + str(srv_profile_id) + ' profile-name ' + srv_profile_name,
                'ont-port ' + 'eth ' + 'adaptive ' + 'pots ' + 'adaptive ' + 'catv ' + 'adaptive',
                'port vlan eth 1 translation ' + vlan_id + ' user-vlan ' + vlan_id,
                'commit',
                'exit'
            ]
        elif type_name == 'sfu_access':
            command_list = [
                'ont-srvprofile gpon profile-id ' + str(srv_profile_id) + ' profile-name ' + srv_profile_name,
                'ont-port ' + 'eth ' + 'adaptive ' + 'pots ' + 'adaptive ' + 'catv ' + 'adaptive',
                'port vlan eth 1 translation ' + vlan_id + ' user-vlan ' + vlan_id,
                'port native-vlan eth 1 ' + vlan_id,
                'commit',
                'exit'
            ]

        else:
            command_list = [
                'ont-srvprofile gpon profile-id ' + str(srv_profile_id) + ' profile-name ' + srv_profile_name,
                'ont-port ' + 'eth ' + 'adaptive ' + 'pots ' + 'adaptive ' + 'catv ' + 'adaptive',
                'port vlan eth 1 transparent',
                'port vlan eth 2 transparent',
                'port vlan eth 3 transparent',
                'port vlan eth 4 transparent',
                'commit',
                'exit'
            ]

        self.connect_ssh(command_list)
        return srv_profile_id

    def cfg_srv_port(self, vlan_id, port, onu_id):
        srv_port_id = 110
        desc = " Created_by_external_script "
        srvport_list = self.output_to_list('show service-port all', re_matchstr=r'  \d+')
        print("Buscando Service-Port correspondente...\n")
        for line in srvport_list:
            if line[2] == vlan_id and line[3] == '0/0/' + port and line[4] == onu_id:
                print("Já existe um service-port do tipo " + line[14] +
                      " configurado para a ONU ID " + onu_id + " na porta " + port)
                print("utilizando o service-port ID " + line[1])
                srv_port_id = line[1]
                return srv_port_id

        print("Não foram encontradas service-ports para esta configuração")

        for line in srvport_list:
            if line[1] == str(srv_port_id):
                srv_port_id = srv_port_id + 1

        srv_port_id = str(srv_port_id)
        print("Criando novo service-port com ID: " + srv_port_id + "\n")

        command_list = ['service-port ' + srv_port_id + ' vlan ' + vlan_id + " gpon 0/0 port " + port + " ont " +
                        onu_id + " gemport 1 multi-service user-vlan " + vlan_id + " tag-action translate ",
                        "service-port desc " + srv_port_id + " " + desc]
        self.connect_ssh(command_list)
        print("Service-port criada")
        return

    def get_port_status(self, port, printthis=False):
        commands = ['interface gpon 0/0',
                    'show port state all']
        attributes = self.output_to_list(commands, re_matchstr=r'^\s+\d/\d\s' + port)
        attributes = attributes[0]

        port_attributes = {'PORT': port,
                           'OPTIC_STATUS': attributes[3],
                           'LINK-STATE': attributes[9],
                           'MTU': attributes[8],
                           'AUTO-FIND': attributes[10],
                           'AUTH-MODE': attributes[11]}

        if printthis:
            df = pd.DataFrame(port_attributes, index=[0])
            header = port_attributes.keys()
            print(tabulate(df, header, showindex=False))
            return port_attributes
        else:
            return port_attributes

    def get_unused_onu_id(self, port, startid=1):
        """
        Function that returns a free index ID at the pon port to be used to register an unauthorizes ONU
        :return: a string with an ONU index value availabe (range: 1-128)
        """

        used_ids = []
        onu_list = self.get_onus_info()
        for onu in onu_list:
            if onu['ONU_ID'] != '-' and onu['PORT'] == port:
                used_ids.append(onu['ONU_ID'])

        onu_id = startid
        while True:
            if str(onu_id) in used_ids:
                onu_id = onu_id + 1
                continue
            else:
                break

        if onu_id <= 128:
            return str(onu_id)
        else:
            print('Não foi possível definir um ONU ID para a porta ' + port +
                  'verifique se a porta está no limite da capacidade')
            return 'port full'

    def cfg_onu(self, pon_sn, config_type, vlan_id, pppoe_username='none', pppoe_password='none', wan_ip_addr='none',
                wan_netmask='none', wan_gateway='none', dns_1='none', dns_2='none', uni_type='none'):

        line_profile_id = self.cfg_line_profile(vlan_id)
        srv_profile_id = self.cfg_srv_profile(vlan_id, config_type)
        onu_params = self.get_onus_info(pon_sn=pon_sn)
        onu_port = onu_params[0]['PORT']
        onu_id = onu_params[0]['ONU_ID']
        wan_index = '0'
        wan_cos = '0'

        if onu_id != '-':
            print('ONU previamente registrada. Limpando configuração prévia da ONU (unregister and register)')
            self.clear_onu_config(pon_sn)
            print('Tentando reautorizar a ONU usando o mesmo index anterior')
            old_onu_id = onu_id
            onu_id = self.get_unused_onu_id('8', int(onu_id))
            if onu_id == old_onu_id:
                print('ONU será reautorizada com o index anterior')
            else:
                print('Não foi possível reautorizar a ONU com o index antrerior, utilizando o valor: ' + onu_id)
        else:
            onu_id = self.get_unused_onu_id('8')
            print(f'ONU desautorizada, autorizando a ONU na porta {onu_port} com o index {onu_id}...')

        cmds = []
        auth_cmd = f'ont add {onu_port} {onu_id} sn-auth {pon_sn} ont-lineprofile-id {line_profile_id} ont-srvprofile-id {srv_profile_id}'
        pppo_cmd = f'ont wan add {onu_port} {onu_id} {wan_index} route voice-internet pppoe username {pppoe_username} password {pppoe_password} vlan-mode tag {vlan_id} priority {wan_cos}'
        dhcp_cmd = f'ont wan add {onu_port} {onu_id} {wan_index} route voice-internet dhcp vlan-mode tag {vlan_id} priority {wan_cos}'
        stat_cmd = f'ont wan add {onu_port} {onu_id} {wan_index} route voice-internet static ip {wan_ip_addr} mask {wan_netmask} gateway {wan_gateway} primary-dns {dns_1} secondary-dns {dns_2} vlan-mode tag {vlan_id} priority {wan_cos}'

        print(config_type)
        if config_type in ['hgu', 'sfu']:
            print('exec sfu or hgu')
            cmds = ['interface gpon 0/0', auth_cmd, 'exit']
        elif config_type == 'pppoe':
            print('exec pppoe')
            cmds = ['interface gpon 0/0', auth_cmd, pppo_cmd, 'exit']
        elif config_type == 'dhcp':
            print('exec dhcp')
            cmds = ['interface gpon 0/0', auth_cmd, dhcp_cmd, 'exit']
        elif config_type == 'static':
            print('exec static')
            cmds = ['interface gpon 0/0', auth_cmd, stat_cmd, 'exit']

        self.connect_ssh(cmds)
        self.cfg_srv_port(vlan_id, onu_port, onu_id)
        print('Comandos de provisionamento executados')
