import json
import os
netlist_path = "c17.json"

with open(netlist_path, 'r') as file:
            netlist = json.load(file)

modulos = netlist.get("modules", netlist)
mod_name = list(modulos.keys())
modulo_nome = mod_name[0] # nome do modulo
print(modulo_nome)


mod_c17 = netlist.get("modules", netlist).get("c17")
portas = mod_c17.get("ports") # pegando as portas
print(list(portas.keys()))