#!/usr/bin/env python3
"""
pyverilog_extractor.py

Extrai a AST do código Verilog usando Pyverilog e organiza informações dos módulos,
portas (inputs, outputs e inouts) e conexões em um dicionário.
Também permite salvar essa estrutura em um arquivo JSON para análises futuras.
"""

import json
from pyverilog.vparser.parser import parse
import pyverilog.vparser.ast as vast

class VerilogExtractor:
    def __init__(self):
        self.structure = {}

    def extract(self, verilog_file):
        """Extrai a AST do arquivo Verilog e organiza a estrutura em um dicionário."""
        ast_root, _ = parse([verilog_file])
        modules_info = {}

        for module in ast_root.description.definitions:
            if isinstance(module, vast.ModuleDef):
                mod_name = module.name
                mod_info = {"ports": {}, "connections": []}

                # Primeiro, inicializa as portas com os nomes listados na portlist (se houver)
                if module.portlist:
                    for port in module.portlist.ports:
                        # Se for Ioport, ele já contém a definição
                        if isinstance(port, vast.Ioport) and hasattr(port.first, 'name'):
                            inner = port.first
                            mod_info["ports"][inner.name] = {"direction": None, "width": 1}
                        elif isinstance(port, vast.Port) and hasattr(port, 'name'):
                            mod_info["ports"][port.name] = {"direction": None, "width": 1}

                # Agora, percorre as declarações (Decl) para identificar o tipo (input/output/inout)
                for item in module.items:
                    if isinstance(item, vast.Decl):
                        for decl in item.list:
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

                # (Opcional) Extração de conexões (atribuições contínuas) pode ser adicionada aqui

                modules_info[mod_name] = mod_info
        self.structure = {"modules": modules_info}
        return self.structure

    def save_json(self, output_file):
        """Salva a estrutura extraída em um arquivo JSON."""
        if not self.structure:
            raise ValueError("Nenhuma estrutura extraída. Execute extract() primeiro.")
        with open(output_file, "w") as f:
            json.dump(self.structure, f, indent=2)

# Exemplo de uso:
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python pyverilog_extractor.py <arquivo_verilog> [<saida_json>]")
    else:
        extractor = VerilogExtractor()
        structure = extractor.extract(sys.argv[1])
        if len(sys.argv) >= 3:
            extractor.save_json(sys.argv[2])
            print(f"Estrutura salva em {sys.argv[2]}")
        else:
            print(json.dumps(structure, indent=2))
