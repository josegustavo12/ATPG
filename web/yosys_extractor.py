import json
import subprocess
import os

class YosysExtractor:
    def __init__(self):
        self.structure = {}

    def createjson(self, verilog_file):
        """Executa o Yosys para gerar um arquivo JSON a partir do arquivo Verilog."""
        if not os.path.exists(verilog_file):
            raise FileNotFoundError("Arquivo não encontrado: " + verilog_file)
        yosys_json = verilog_file.replace(".v", ".json")
        print(f"Gerando arquivo JSON: {yosys_json}")
        cmd = f"yosys -p \"read_verilog {verilog_file}; hierarchy -check; write_json {yosys_json}\""
        print("Comando:", cmd)
        subprocess.run(cmd, shell=True, check=True)
        return yosys_json

    def getLastModuleName(self, yosys_json):
        """Retorna o nome do último módulo encontrado no JSON."""
        with open(yosys_json, "r") as arquivo:
            dados = json.load(arquivo)
            modules = list(dados["modules"].keys())
            if not modules:
                raise ValueError("Nenhum módulo encontrado no arquivo JSON.")
            return modules[-1]

    def getInputs(self, yosys_json):
        """Retorna a lista de portas de entrada do último módulo."""
        mod_name = self.getLastModuleName(yosys_json)
        with open(yosys_json, "r") as json_file:
            dados = json.load(json_file)
            ports = dados["modules"][mod_name]["ports"]
            input_ports = [port for port, info in ports.items() if info["direction"] == "input"]
            return input_ports

    def getOutputs(self, yosys_json):
        """Retorna a lista de portas de saída do último módulo."""
        mod_name = self.getLastModuleName(yosys_json)
        with open(yosys_json, "r") as json_file:
            dados = json.load(json_file)
            ports = dados["modules"][mod_name]["ports"]
            output_ports = [port for port, info in ports.items() if info["direction"] == "output"]
            return output_ports

    def getWires(self, yosys_json):
        """Retorna a lista de fios (netnames) do último módulo, excluindo as portas."""
        mod_name = self.getLastModuleName(yosys_json)
        with open(yosys_json, "r") as arquivo:
            dados = json.load(arquivo)
            mod = dados["modules"][mod_name]
            netnames = mod.get("netnames", {})
            nomes_ports = list(mod["ports"].keys())
            wires = [nome_net for nome_net, info_net in netnames.items()
                     if info_net.get("hide_name", 1) == 0 and nome_net not in nomes_ports]
        return wires

    def getGates(self, yosys_json):
        """Retorna a lista de células (gates) do último módulo."""
        mod_name = self.getLastModuleName(yosys_json)
        with open(yosys_json, "r") as arquivo:
            dados = json.load(arquivo)
            cells = dados["modules"][mod_name].get("cells", {})
            return list(cells.keys())

    def getMod(self, yosys_json):
        """Retorna o nome do último módulo."""
        return self.getLastModuleName(yosys_json)

    def extract(self, yosys_json):
        """Extrai a estrutura completa do arquivo JSON gerado pelo Yosys."""
        extracted = {
            "inputs": self.getInputs(yosys_json),
            "outputs": self.getOutputs(yosys_json),
            "wires": self.getWires(yosys_json),
            "module": self.getMod(yosys_json),
            "gates": self.getGates(yosys_json)
        }
        self.structure = extracted
        return extracted
