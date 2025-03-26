from generate_testbench import GenerateTB
import os
import subprocess
import matplotlib.pyplot as plt

class Simulador:
    def __init__(self, netlist):
        """
        Inicializa o simulador com a netlist.
        Essa netlist é utilizada para extrair as entradas, saídas e o nome do módulo.
        """
        self.tb_gen = GenerateTB(netlist)
    
    def run_modelsim(self, modulos_file, design_file, tb_filename, top_module):
        """
        Compila o design e o testbench usando o ModelSim e executa a simulação.
        Retorna a saída da simulação.
        """

        # Compila os arquivos com vlog
        cmd_compile = ["vlog", modulos_file, design_file, tb_filename]
        print("Compilando com ModelSim:", " ".join(cmd_compile))
        result_compile = subprocess.run(cmd_compile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result_compile.returncode != 0:
            print("Erro na compilação:")
            print(result_compile.stderr)
            return None

        # Executa a simulação com vsim em modo de linha de comando.
        cmd_simulate = f'vsim -c -do "run -all; quit" {top_module}'
        print("Executando simulação com ModelSim:", cmd_simulate)
        result_sim = subprocess.run(cmd_simulate, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print(result_sim.stdout)
        if result_sim.returncode != 0:
            print("Erro na simulação:")
            print(result_sim.stderr)
            return None
        return result_sim.stdout
        
    def run_iverilog(self, modulos_file, design_file, tb_filename, top_module):
        """
        Compila o design e o testbench usando o Icarus Verilog e executa a simulação.
        Retorna a saída da simulação.
        """
        # Define o nome do arquivo executável da simulação
        output_file = "sim.out"
        
        # Monta o comando de compilação com iverilog
        cmd_compile = ["iverilog", "-o", output_file]
        if top_module:
            cmd_compile.extend(["-s", top_module])
        
        # Se o design e os módulos estiverem no mesmo arquivo, não os incluímos duas vezes.
        if modulos_file == design_file:
            cmd_compile.extend([design_file, tb_filename])
        else:
            cmd_compile.extend([modulos_file, design_file, tb_filename])
            
        print("Compilando com Icarus Verilog:", " ".join(cmd_compile))
        
        result_compile = subprocess.run(cmd_compile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result_compile.returncode != 0:
            print("Erro na compilação:")
            print(result_compile.stderr)
            return None

        # Executa a simulação usando vvp
        cmd_simulate = ["vvp", output_file]
        print("Executando simulação com Icarus Verilog:", " ".join(cmd_simulate))
        
        result_sim = subprocess.run(cmd_simulate, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print(result_sim.stdout)
        if result_sim.returncode != 0:
            print("Erro na simulação:")
            print(result_sim.stderr)
            return None
        return result_sim.stdout

    def parse_output(self, sim_output):
        """
        Processa a saída da simulação, procurando linhas que contenham 'OUTPUT:'.
        Espera linhas no formato: "<num_vetor>. OUTPUT: <sinal> = <valor>"
        Retorna um dicionário no formato:
        { "1": {<sinal>: <valor>, ...}, "2": {<sinal>: <valor>, ...}, ... }
        """
        # Debug: imprime o sim_output completo
        print("Conteúdo completo da saída da simulação:")
        print(sim_output)
        
        results = {}
        for line in sim_output.splitlines():
            if "OUTPUT:" in line:
                try:
                    # Divide a linha em duas partes usando ". OUTPUT:" como separador
                    parts = line.split(". OUTPUT:", 1)
                    if len(parts) == 2:
                        vec_index = parts[0].strip()  # Número do vetor, por exemplo "1"
                        rest = parts[1].strip()       # Deve ser algo como "sinal = valor"
                        
                        # Divide a parte restante no sinal e valor
                        subparts = rest.split("=", 1)
                        if len(subparts) == 2:
                            signal = subparts[0].strip()
                            value = subparts[1].strip()
                            
                            # Agrupa os resultados por vetor
                            if vec_index not in results:
                                results[vec_index] = {}
                            results[vec_index][signal] = value
                except Exception as e:
                    print("Erro ao processar linha:", line, e)
        return results
    
    def analyze_atpg_results(self, results):
        """
        Analisa os resultados de simulação para ATPG.
        
        Parâmetros:
        results: dicionário com a seguinte estrutura:
            Caso numero_falhas == 1:
            {
                'sem_falhas': { '1': {<sinal>: <valor>, ...}, ... },
                'com_falhas': { '1': {<sinal>: <valor>, ...}, ... }
            }
            Caso numero_falhas > 1:
            {
                'sem_falhas': { '1': {<sinal>: <valor>, ...}, ... },
                'com_falhas': [ { '1': {<sinal>: <valor>, ...}, ... },
                                { '1': {<sinal>: <valor>, ...}, ... },
                                ... ]
            }
        
        Retorna um dicionário com a análise.
        Quando houver múltiplas simulações de falha, adiciona o campo 'detection_percentage'
        que é a porcentagem de simulações (falhas injetadas) que foram detectadas.
        """
        sem_falhas = results.get("sem_falhas", {})
        com_falhas = results.get("com_falhas", None)
        
        # Se com_falhas for um dicionário (única simulação), processa como antes:
        if isinstance(com_falhas, dict):
            total_vectors = len(sem_falhas)
            discrepancy_count = 0
            total_signals_compared = 0
            total_differences = 0
            vector_discrepancies = {}
            
            # Itera sobre cada vetor presente em sem_falhas
            for vec_id, sem_values in sem_falhas.items():
                com_values = com_falhas.get(vec_id, {})
                differences = {}
                for signal, sem_val in sem_values.items():
                    total_signals_compared += 1
                    com_val = com_values.get(signal, None)
                    if com_val is None or sem_val != com_val:
                        differences[signal] = (sem_val, com_val)
                        total_differences += 1
                if differences:
                    discrepancy_count += 1
                    vector_discrepancies[vec_id] = {
                        "num_differences": len(differences),
                        "differences": differences
                    }
            
            discrepancy_percentage = (discrepancy_count / total_vectors * 100) if total_vectors > 0 else 0

            analysis = {
                "total_vectors": total_vectors,
                "vectors_with_discrepancy": discrepancy_count,
                "discrepancy_percentage": discrepancy_percentage,
                "total_signals_compared": total_signals_compared,
                "total_differences": total_differences,
                "vector_discrepancies": vector_discrepancies
            }
            return analysis
        
        # Caso com_falhas seja uma lista (múltiplas simulações de falha):
        elif isinstance(com_falhas, list):
            total_faults = len(com_falhas)
            detection_count = 0
            simulation_details = {}
            overall_total_signals_compared = 0
            overall_total_differences = 0
            
            # Para cada simulação com falha, compara com a simulação sem falha
            for i, fault_result in enumerate(com_falhas):
                vec_discrepancies = {}
                discrepancy_count = 0
                total_signals = 0
                total_diffs = 0
                for vec_id, sem_values in sem_falhas.items():
                    differences = {}
                    # Garante que fault_result tenha resultados para o mesmo vetor
                    fault_vec = fault_result.get(vec_id, {})
                    for signal, sem_val in sem_values.items():
                        total_signals += 1
                        fault_val = fault_vec.get(signal, None)
                        if fault_val is None or sem_val != fault_val:
                            differences[signal] = (sem_val, fault_val)
                            total_diffs += 1
                    if differences:
                        discrepancy_count += 1
                        vec_discrepancies[vec_id] = {
                            "num_differences": len(differences),
                            "differences": differences
                        }
                if discrepancy_count > 0:
                    detection_count += 1
                simulation_details[f"fault_simulation_{i}"] = {
                    "vectors_with_discrepancy": discrepancy_count,
                    "total_signals_compared": total_signals,
                    "total_differences": total_diffs,
                    "vector_discrepancies": vec_discrepancies
                }
                overall_total_signals_compared += total_signals
                overall_total_differences += total_diffs
            
            detection_percentage = (detection_count / total_faults * 100) if total_faults > 0 else 0
            total_vectors = len(sem_falhas)
            
            analysis = {
                "total_vectors": total_vectors,
                "total_fault_simulations": total_faults,
                "detected_faults": detection_count,
                "detection_percentage": detection_percentage,
                "overall_total_signals_compared": overall_total_signals_compared,
                "overall_total_differences": overall_total_differences,
                "simulation_details": simulation_details
            }
            return analysis
        else:
            print("Formato dos resultados com falha não reconhecido.")
            return None

    def simulate(self, modulos_file, design_file, vector=None, fault_port=None, fault_value=None, top_module="tb", clock=False, numero_falhas=1):
        """
        Executa a simulação com o vetor de teste fornecido duas vezes:
        - Sem injeção de falha.
        - Com injeção de falha, podendo ser executada múltiplas vezes se numero_falhas > 1.
        
        Parâmetros:
        - design_file: arquivo do design em Verilog.
        - vector: dicionário com os valores de teste para as entradas.
        - fault_port: nome do sinal onde a falha será injetada.
        - fault_value: valor forçado (True para stuck at 1, False para stuck at 0).
        - top_module: nome do módulo top do testbench.
        - clock: se True, adiciona um clock ao testbench.
        - numero_falhas: número de falhas a serem injetadas.
        
        Retorna:
        - dicionário contendo os resultados de ambas as simulações, por exemplo:
            {
                "sem_falhas": resultado_sem_falhas,
                "com_falhas": resultado_com_falhas   # pode ser um dicionário ou uma lista, conforme numero_falhas
            }
        """
        # Simulação sem falha
        tb_filename_sem = "tb_generated.v"
        self.tb_gen.create_testbench(vector, tb_filename_sem, fault=False, clock=clock)
        sim_output_sem = self.run_iverilog(modulos_file, design_file, tb_filename_sem, top_module)
        results_sem = self.parse_output(sim_output_sem) if sim_output_sem else None
        
        # Apaga o arquivo de testbench sem falha
        if os.path.exists(tb_filename_sem):
            os.remove(tb_filename_sem)

        # Simulação com falha (pode ser única ou múltipla)
        if numero_falhas <= 1:
            tb_filename_fault = "tb_fault.v"
            self.tb_gen.create_testbench(vector, tb_filename_fault, fault=True, fault_port=fault_port, fault_value=fault_value, clock=clock)
            sim_output_com = self.run_iverilog(modulos_file, design_file, tb_filename_fault, top_module)
            results_com = self.parse_output(sim_output_com) if sim_output_com else None
        else:
            results_com = []
            # Para cada falha, gera um arquivo de testbench diferente.
            for i in range(numero_falhas):
                tb_filename_fault = f"tb_fault_{i}.v"
                # Modifica o nome do sinal de falha para simular falhas diferentes (ex: "N23" -> "N23_0", "N23_1", etc.)
                fault_port_i = f"{fault_port}_{i}" if fault_port is not None else None
                self.tb_gen.create_testbench(vector, tb_filename_fault, fault=True, fault_port=fault_port_i, fault_value=fault_value, clock=clock)
                sim_output_fault = self.run_iverilog(modulos_file, design_file, tb_filename_fault, top_module)
                result_fault = self.parse_output(sim_output_fault) if sim_output_fault else None
                results_com.append(result_fault)

                if os.path.exists(tb_filename_fault):
                            os.remove(tb_filename_fault)
                
        return {"sem_falhas": results_sem, "com_falhas": results_com}
