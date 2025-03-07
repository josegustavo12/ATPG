#!/usr/bin/env python3
"""
simulator.py

Fluxo:
  1. Gera um vetor de teste aleatório (com opção de definir a seed) para as entradas extraídas.
  2. Cria um testbench Verilog automaticamente, instanciando o design usando os nomes das portas
     extraídas do arquivo de netlist (gerado pelo pyverilog_extractor).
  3. Para simular o design "bom", o testbench aplica o vetor gerado e exibe as saídas.
  4. Para simular o design "com falha", o testbench perturba uma porta específica (por exemplo, 'b')
     forçando seu valor oposto.
  5. O Icarus Verilog compila e simula o design e o script processa a saída, comparando os resultados.
"""

import subprocess
import random
import sys
import json
import os

class CombinationalSimulator:
    def __init__(self, netlist, module_name=None):
        """
        Inicializa o simulador com a netlist extraída.
        
        Args:
            netlist (dict): Estrutura extraída pelo pyverilog_extractor.
            module_name (str): Nome do módulo a simular. Se None e houver apenas um módulo, usa-o.
        """
        # Verificação do verilog (posso retirar dps, mas é bom ter)
        modules_dict = netlist.get("modules", netlist)
        if module_name is None:
            mod_names = list(modules_dict.keys())
            if len(mod_names) != 1:
                raise ValueError("Especifique module_name, pois há mais de um módulo na netlist.")
            module_name = mod_names[0]
        if module_name not in modules_dict:
            raise ValueError(f"Módulo '{module_name}' não encontrado na netlist.")
        
        
        self.module_name = module_name
        self.module = modules_dict[module_name]
        
        # Extrai portas de entrada e saída a partir da netlist
        self.input_ports = []
        self.output_ports = []
        for port_name, info in self.module.get("ports", {}).items():
            direc = info.get("direction", "").lower()
            if direc == "input":
                self.input_ports.append(port_name)
            elif direc == "output":
                self.output_ports.append(port_name)
        if not self.input_ports or not self.output_ports:
            print("Aviso: Não foram encontradas portas de entrada ou saída na netlist extraída.")
        print(f"Entradas detectadas: {self.input_ports}")
        print(f"Saídas detectadas: {self.output_ports}")
        
        # Extrai os nomes dos gates, se disponíveis, e mapeia para o net de saída
        self.gate_ports = []
        self.gate_mapping = {}
        if "gates" in self.module:
            for gate in self.module["gates"]:
                if "name" in gate:
                    gate_name = gate["name"]
                    self.gate_ports.append(gate_name)
                    # Assumindo que a instância usa conexão posicional, o primeiro argumento é a saída.
                    conns = gate.get("connections", {})
                    if conns:
                        # Usa o primeiro net conectado como saída
                        out_net = list(conns.values())[0]
                        self.gate_mapping[gate_name] = out_net
            if self.gate_ports:
                print(f"Gates detectados: {self.gate_ports}")
                print(f"Mapeamento de gates para nets: {self.gate_mapping}")
            else:
                print("Nenhum gate detectado no design.")
        else:
            print("Nenhum gate detectado no design.")
    
        # Extrai os nomes dos gates, se disponíveis
        # Aqui assume-se que a netlist possui uma chave "gates" com uma lista de instâncias
        
        self.gate_ports = []
        if "gates" in self.module:
            # Cada instância de gate é um dicionário que deve ter a chave "name"
            self.gate_ports = [gate["name"] for gate in self.module["gates"] if "name" in gate]
            if self.gate_ports:
                print(f"Gates detectados: {self.gate_ports}")
            else:
                print("Nenhum gate detectado no design.")
        else:
            print("Nenhum gate detectado no design.")
    def generate_random_vector(self, seed=None): # possivel melhora aqui
        """Gera um vetor de teste aleatório para as entradas extraídas."""
        if seed is not None:
            random.seed(seed)
        vector = {}
        for inp in self.input_ports:
            vector[inp] = random.choice([0, 1])
        return vector

    def generate_random_vectors(self, count=1, seed=None):
        """Gera uma lista de vetores aleatórios."""
        if seed is not None:
            random.seed(seed)
        return [self.generate_random_vector() for _ in range(count)]

    def create_testbench(self, vector, tb_filename, fault=False, fault_port=None):
        """
        Cria um testbench Verilog que instancia o design e aplica o vetor de teste.
        Se fault=True, injeta a falha no sinal fault_port, forçando um valor:
        - Se fault_port é uma porta de entrada: força o valor oposto.
        - Se fault_port é uma porta de saída: usa 'force' para fixar o valor a 0.
        - Se fault_port é uma porta de gate (ex.: AND3_0): força a porta de saída (assumindo "Y")
          a 0.
        - Se fault_port não é declarado externamente, assume-se que é um net interno e usa
          referência hierárquica (ex.: uut.<fault.port>).
        """
        tb_lines = []
        tb_lines.append("`timescale 1ns/1ps")
        tb_lines.append("module tb;")
        
        
        # Declara as entradas e saídas com base na netlist extraída
        for inp in self.input_ports:
            tb_lines.append(f"  reg {inp};")
        for out in self.output_ports:
            tb_lines.append(f"  wire {out};")
        tb_lines.append("")
        """
          reg N1;
          reg N2;
          ...
          wire N10;
          wire N11;
        """
        
        
        # Instancia o design; assume que o nome do módulo é self.module_name
        conns = ", ".join([f".{p}({p})" for p in (self.input_ports + self.output_ports)])
        tb_lines.append(f"  {self.module_name} uut ({conns});")
        
        """
          c17 uut (.N1(N1), .N2(N2), .N10(N10), .N11(N11)); // instanciando o módulo
        """
        
        tb_lines.append("")
        tb_lines.append("  initial begin")
        # Aplica os valores de entrada do vetor
        for inp in self.input_ports:
            tb_lines.append(f"    {inp} = {vector[inp]};")
        """
          N1 = 1; // aplica os vetores correspondentes a cada entrada
          N2 = 0;
          N3 = 1;
          ...
        """   
            
            
        # injeção de falha se o parametro fault_port for True
        if fault and fault_port:
    
            tb_lines.append("    #5;") # aguarda 5 unidades pra injetar a falha
            if fault_port in self.input_ports:
                # Para entradas: força o valor oposto
                original = vector[fault_port]
                forced = 0 if original == 1 else 1
                tb_lines.append(f"    {fault_port} = {forced};  // Falha em porta de entrada: força valor oposto")
                """
                N1 = 1; // valor inicial correto
                N1 = 0;  // Falha em porta de entrada: força valor oposto
                """
            elif fault_port in self.output_ports:
                # Para saídas: força diretamente o valor 0
                tb_lines.append(f"    force {fault_port} = 0;  // Falha em porta de saída: força valor 0")
                """
                  force N10 = 0;  // Falha em porta de saída: força valor 0 (nesse caso precisaria usar o force)
                """
                
            elif fault_port in self.gate_ports:
                # Para um gate: utiliza o mapeamento para injetar falha no net de saída
                out_net = self.gate_mapping.get(fault_port)
                if out_net:
                    tb_lines.append(f"    force uut.{out_net} = 0;  // Falha em porta lógica: força net de saída '{out_net}' a 0")
                else:
                    tb_lines.append(f"    // Aviso: não foi possível mapear o gate '{fault_port}' para um net de saída")
            else:
                # Caso o sinal não seja declarado externamente, assume-se que é um net interno
                tb_lines.append(f"    force uut.{fault_port} = 0;  // Falha em net interno: força valor 0")
       
                """
                  force uut.AND3_0 = 0;  // Falha em porta lógica: força saída a 0
                """
        tb_lines.append("    #10;")
        # Imprime as saídas usando $display (formato: OUTPUT: <sinal> = <valor>)
        for out in self.output_ports:
            tb_lines.append(f'    $display("OUTPUT: {out} = %b", {out});')
        tb_lines.append("    $finish;")
        tb_lines.append("  end")
        tb_lines.append("endmodule")
        with open(tb_filename, "w") as f:
            f.write("\n".join(tb_lines))
        print(f"Testbench gerado em {tb_filename}")
        
        # codigo gerado no final
        """"
                `timescale 1ns/1ps
        module tb;
        
        reg N1;    // Exemplo: sinal de entrada N1
        reg N2;    // Exemplo: sinal de entrada N2
        
        wire N10;  // Exemplo: sinal de saída N10
        wire N11;  // Exemplo: sinal de saída N11
        
        c17 uut (.N1(N1), .N2(N2), .N10(N10), .N11(N11));

        initial begin
            N1 = 1;  // Sinal N1 recebe valor 1
            N2 = 0;  // Sinal N2 recebe valor 0
            
            #5;
            
            force N10 = 0;  // Força a saída N10 a assumir o valor 0

            #10;
            
            $display("OUTPUT: N10 = %b", N10);  // Exibe o valor de N10
            $display("OUTPUT: N11 = %b", N11);  // Exibe o valor de N11

            $finish;
        end
        endmodule

        """





    def run_iverilog(self, design_file, tb_filename, output_exe="sim.out"):
        """Compila o design com o testbench usando Icarus Verilog."""
        cmd = ["iverilog", "-o", output_exe, design_file, tb_filename]
        print("Compilando:", " ".join(cmd))
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            print("Erro na compilação:")
            print(result.stderr)
            return None
        return output_exe

    def run_vvp(self, sim_exe):
        """Executa a simulação com vvp e retorna a saída."""
        cmd = ["vvp", sim_exe]
        print("Executando simulação:", " ".join(cmd))
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            print("Erro na simulação:")
            print(result.stderr)
            return None
        return result.stdout

    def parse_output(self, sim_output):
        """
        Processa a saída da simulação, procurando linhas que começam com 'OUTPUT:'.
        Retorna um dicionário {nome_do_sinal: valor}.
        """
        results = {}
        for line in sim_output.splitlines():
            if line.startswith("OUTPUT:"):
                try:
                    _, rest = line.split("OUTPUT:", 1)
                    parts = rest.split("=")
                    if len(parts) == 2:
                        signal = parts[0].strip()
                        value = parts[1].strip()
                        results[signal] = value
                except Exception as e:
                    print("Erro ao processar linha:", line, e)
        return results

    def simulate(self, design_file, vector, fault=False, fault_port=None):
        """
        Executa a simulação com o vetor de teste. Se fault=True, gera o testbench com a porta perturbada.
        Retorna os resultados da simulação (dicionário de saídas).
        """
        tb_filename = "tb_fault.v" if fault else "tb_good.v"
        self.create_testbench(vector, tb_filename, fault=fault, fault_port=fault_port)
        sim_exe = self.run_iverilog(design_file, tb_filename)
        if sim_exe is None:
            return None
        sim_output = self.run_vvp(sim_exe)
        if sim_output is None:
            return None
        results = self.parse_output(sim_output)
        # Remove arquivos temporários
        if os.path.exists(tb_filename):
            os.remove(tb_filename)
        if os.path.exists(sim_exe):
            os.remove(sim_exe)
        return results
    
    def get_infos(self):
        num_gates = len(self.module.get("gates", {}))
        num_entradas = len(self.input_ports)
        num_saidas = len(self.output_ports)
        return num_gates, num_entradas, num_saidas



# função de teste
def main():
    if len(sys.argv) < 3:
        print("Uso: python simulator.py <netlist.json> <design.v> [--seed SEED]")
        sys.exit(1)
    netlist_file = sys.argv[1]
    design_file = sys.argv[2]
    seed = None
    if "--seed" in sys.argv:
        idx = sys.argv.index("--seed")
        try:
            seed = int(sys.argv[idx+1])
        except:
            seed = None

    with open(netlist_file, "r") as f:
        netlist = json.load(f)

    try:
        simulator = CombinationalSimulator(netlist)
    except Exception as e:
        print("Erro ao inicializar o simulador:", e)
        sys.exit(1)

    # Gera vetor de teste aleatório
    test_vector = simulator.generate_random_vector(seed=seed)
    print("Vetor de entrada gerado:", test_vector)

    # Simula o design bom
    print("\nSimulação do design bom:")
    good_results = simulator.simulate(design_file, test_vector, fault=False)
    if good_results is None:
        print("Erro na simulação do design bom.")
        sys.exit(1)
    print("Resultados (bom):", good_results)

    # Simula o design com falha (perturba a porta 'b')
    print("\nSimulação do design com falha (porta 'b' perturbada):")
    fault_results = simulator.simulate(design_file, test_vector, fault=True, fault_port="b")
    if fault_results is None:
        print("Erro na simulação do design com falha.")
        sys.exit(1)
    print("Resultados (falha):", fault_results)

    if good_results != fault_results:
        print("\nA falha foi detectada: os resultados diferem.")
    else:
        print("\nFalha não detectada: os resultados são idênticos.")

if __name__ == "__main__":
    main()
