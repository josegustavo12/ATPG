#!/usr/bin/env python3
"""
pyverilog_extractor.py

Extrai a AST do código Verilog usando Pyverilog e organiza informações dos módulos,
portas (inputs, outputs e inouts), wires, conexões e gates em um dicionário.
Salva essa estrutura em um arquivo JSON para análises futuras.
"""

import json
from pyverilog.vparser.parser import parse
import pyverilog.vparser.ast as vast  # manipular os nós

class VerilogExtractor:
    def __init__(self):
        self.structure = {}

    def extract(self, verilog_file):
        # Extrai a AST do arquivo Verilog e organiza a estrutura em um dicionário.
        ast_root, _ = parse([verilog_file])
        modules_info = {}

        # Lista de nomes dos gates primitivos
        gate_primitives = {"and", "nand", "or", "nor", "not", "buf", "xor", "xnor"}

        for module in ast_root.description.definitions:
            if isinstance(module, vast.ModuleDef):
                mod_name = module.name
                mod_info = {"ports": {}, "wires": {}, "connections": [], "gates": []}

                # Inicializa as portas com os nomes listados na portlist (se houver)
                if module.portlist:
                    # "ioport" é o nó que pode encapsular a declaração da porta e "inner" se refere ao nó interno
                    for port in module.portlist.ports:
                        # Se for Ioport, ele já contém a definição
                        if isinstance(port, vast.Ioport) and hasattr(port.first, 'name'):
                            inner = port.first
                            mod_info["ports"][inner.name] = {"direction": None, "width": 1}
                        elif isinstance(port, vast.Port) and hasattr(port, 'name'):
                            mod_info["ports"][port.name] = {"direction": None, "width": 1}

                # Percorre as declarações para identificar o tipo das portas e wires
                for item in module.items:
                    if isinstance(item, vast.Decl):
                        for decl in item.list:
                            # Extração de portas: inputs, outputs e inouts
                            if isinstance(decl, (vast.Input, vast.Output, vast.Inout)) and hasattr(decl, 'name'):
                                width = 1
                                if decl.width:
                                    try:
                                        msb = int(decl.width.msb.value)
                                        lsb = int(decl.width.lsb.value)
                                        width = abs(msb - lsb) + 1
                                    except Exception:
                                        width = 1
                                direction = ("input" if isinstance(decl, vast.Input)
                                             else "output" if isinstance(decl, vast.Output)
                                             else "inout")
                                mod_info["ports"][decl.name] = {"direction": direction, "width": width}
                            # Extração de wires: nets internos não declarados como porta
                            elif isinstance(decl, vast.Wire) and hasattr(decl, 'name'):
                                width = 1
                                if decl.width:
                                    try:
                                        msb = int(decl.width.msb.value)
                                        lsb = int(decl.width.lsb.value)
                                        width = abs(msb - lsb) + 1
                                    except Exception:
                                        width = 1
                                mod_info["wires"][decl.name] = {"width": width}

                    # Extração de instâncias de gates
                    if isinstance(item, vast.InstanceList):
                        # Obtém o nome do módulo instanciado (pode ser um identificador ou string)
                        inst_module = item.module
                        if hasattr(inst_module, 'name'):
                            inst_module = inst_module.name
                        # Verifica se é um gate primitivo
                        if inst_module in gate_primitives:
                            for instance in item.instances:
                                gate_info = {
                                    "name": instance.name,
                                    "type": inst_module,
                                    "connections": {}
                                }
                                # Percorre as conexões dos ports
                                if instance.portlist:
                                    for port_arg in instance.portlist:
                                        port_name = port_arg.portname
                                        # Tenta extrair o nome do sinal conectado
                                        if hasattr(port_arg.argname, 'name'):
                                            conn_name = port_arg.argname.name
                                        else:
                                            conn_name = str(port_arg.argname)
                                        gate_info["connections"][port_name] = conn_name
                                mod_info["gates"].append(gate_info)

                    # Em alguns netlists ISCAS89 os instanciamentos aparecem como nós do tipo Gate.
                    if hasattr(vast, 'Gate') and isinstance(item, vast.Gate):
                        gate_info = {
                            "name": item.name,
                            "type": item.gatetype if hasattr(item, 'gatetype') else "unknown",
                            "connections": {}
                        }
                        if item.portlist:
                            for port_arg in item.portlist:
                                port_name = port_arg.portname
                                if hasattr(port_arg.argname, 'name'):
                                    conn_name = port_arg.argname.name
                                else:
                                    conn_name = str(port_arg.argname)
                                gate_info["connections"][port_name] = conn_name
                        mod_info["gates"].append(gate_info)


                modules_info[mod_name] = mod_info
        self.structure = {"modules": modules_info}
        return self.structure

    def save_json(self, output_file):
        """Salva a estrutura extraída em um arquivo JSON."""
        if not self.structure:
            raise ValueError("Nenhuma estrutura extraída. Execute extract() primeiro.")
        with open(output_file, "w") as f:
            json.dump(self.structure, f, indent=2)
