from g8psx import G8PSX
import re
from tabulate import tabulate


def read_scenarios(wan_type):
    # le o arquivo cenarios e cria uma lista com as configurações disponíveis com base no tipo escolhido (PPPoE,
    # DHCP, estático e etc). Então para cada linha é criada uma lista de atributos (line_scenario), e salva essas
    # listas em outra lista (scenariolist)

    file = "cenarios"
    scenariolist = []

    with open(file, 'r', encoding='UTF-8') as scenariofile:
        scenariofile = scenariofile.read().splitlines()

    for line in scenariofile:
        if line.startswith(wan_type):
            stripped_line = line.strip(" ")
            line_scenario = stripped_line.split()
            scenariolist.append(line_scenario)
    return scenariolist


def mainmenu():
    print("Escolha o modo de configuração do cenário:\n")
    print(
        "1-PPPoE\n2-DHCP\n3-IP estático\n4-Bridge SFU\n5-Router HGU - Sem tentativa de configuração de wan via OMCI\n")
    menu_header = []
    scenariolist = []
    valid_input = False
    while not valid_input:
        option = input("Digite número da opção: ")
        if option == "1":
            scenariolist = read_scenarios("pppoe")
            menu_header = ["ID", "Type", "VLAN", "PPPOE_USER", "PPPOE_PASSWD"]
            valid_input = True
        elif option == "2":
            scenariolist = read_scenarios("dhcp")
            menu_header = ["ID", "type", "VLAN"]
            valid_input = True
        elif option == "3":
            scenariolist = read_scenarios("static")
            menu_header = ["ID", "type", "VLAN", "WAN_IP_ADDR", "WAN_NETMASK", "WAN_GATEWAY", "DNS_1", "DNS_2"]
            valid_input = True
        elif option == "4":
            scenariolist = read_scenarios("sfu")
            menu_header = ["ID", "type", "VLAN", "UNI ENCAPSULATION"]
            valid_input = True
        elif option == "5":
            scenariolist = read_scenarios("hgu")
            menu_header = ["ID", "type", "VLAN"]
            valid_input = True
        else:
            print("opção inválida")

    # code to add an option ID to the list of scenarios (each scenario in scenariolist)
    scenario_id = 0

    for scenario in scenariolist:
        scenario_id = scenario_id + 1
        scenario.insert(0, str(scenario_id))

    print("Lista de cenários:\n")
    print(tabulate(scenariolist, menu_header))

    scenario_id = int(input("\n\nID do cenário: "))
    scenario = scenariolist[scenario_id - 1]
    return scenario


mainmenu()
