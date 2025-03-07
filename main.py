#!/usr/bin/env python3
"""
main.py (Modificado)

Fluxo simplificado para simulações:
  1. Extrai a estrutura do design Verilog (arquivo fixo 'design.v').
  2. Inicializa o simulador combinacional.
  3. Permite especificar o tipo de sinal para injeção de falha (gate, input, output ou wire).
  4. Seleciona aleatoriamente um sinal do tipo escolhido.
  5. Executa simulações com vetores aleatórios.
  6. Calcula e exibe estatísticas de detecção, mostrando o sinal injetado.
"""

import json
import random
from simulacao.pyverilog_extractor import VerilogExtractor
from simulacao.simulator import CombinationalSimulator
from utils.data_utils import *
import time as t

def main():
    # Configurações fixas
    DESIGN_VERILOG = "verilog/c6288.v"
    NUM_SIMULATIONS = 100

    # FAULT_TYPE: defina o tipo de sinal para injeção de falha.
    # Opções: "gate", "input", "output" ou "wire"
    FAULT_TYPE = "gate"

    # Etapa 1: Extração da netlist do design
    print("Extraindo estrutura do design...")
    extractor = VerilogExtractor()
    try:
        netlist = extractor.extract(DESIGN_VERILOG)
        extractor.save_json("simulacao/data/netlist.json")
    except Exception as e:
        print(f"Erro na extração: {e}")
        return

    # Seleciona o primeiro módulo encontrado na netlist
    modules = list(netlist["modules"].keys())
    if not modules:
        print("Nenhum módulo encontrado na netlist.")
        return
    module_name = modules[0]

    # Etapa 2: Inicialização do simulador combinacional
    try:
        simulator = CombinationalSimulator(netlist, module_name=module_name)
    except Exception as e:
        print(f"Erro na inicialização do simulador: {e}")
        return

    # Etapa 3: Seleção do sinal para injeção de falha
    fault_signal = None
    if FAULT_TYPE == "gate":
        if simulator.gate_ports:
            fault_signal = random.choice(simulator.gate_ports)
        else:
            print("Nenhum gate disponível para injeção de falha. Verifique a netlist.")
            return
    elif FAULT_TYPE == "input":
        if simulator.input_ports:
            fault_signal = random.choice(simulator.input_ports)
        else:
            print("Nenhum input disponível para injeção de falha. Verifique a netlist.")
            return
    elif FAULT_TYPE == "output":
        if simulator.output_ports:
            fault_signal = random.choice(simulator.output_ports)
        else:
            print("Nenhum output disponível para injeção de falha. Verifique a netlist.")
            return
        
    # wire ainda não está funcionando 100%
    elif FAULT_TYPE == "wire":
        # Para wires, acessamos o dicionário 'wires' extraído pelo VerilogExtractor
        wires = netlist["modules"][module_name].get("wires", {})
        if wires:
            fault_signal = random.choice(list(wires.keys()))
        else:
            print("Nenhum wire disponível para injeção de falha. Verifique a netlist.")
            return
    else:
        print(f"FAULT_TYPE '{FAULT_TYPE}' desconhecido. Use 'gate', 'input', 'output' ou 'wire'.")
        return

    print(f"Sinal selecionado para injeção de falha ({FAULT_TYPE}): {fault_signal}")

    # Etapa 4: Execução das simulações
    print(f"\nIniciando {NUM_SIMULATIONS} simulações com falha no sinal '{fault_signal}'...")
    detected_count = 0
    inicio = t.time()
    for i in range(NUM_SIMULATIONS):
        # Gera vetor de teste aleatório
        test_vector = simulator.generate_random_vector()
        
        # Simulação sem falha (design bom)
        good_result = simulator.simulate(
            DESIGN_VERILOG,
            test_vector,
            fault=False
        )
        
        # Simulação com falha no sinal selecionado
        fault_result = simulator.simulate(
            DESIGN_VERILOG,
            test_vector,
            fault=True,
            fault_port=fault_signal
        )

        # Comparação dos resultados: se forem diferentes, a falha foi detectada
        if good_result and fault_result and good_result != fault_result:
            detected_count += 1

        print(f"Simulação {i+1}/{NUM_SIMULATIONS} concluída.")
    
    fim = t.time()
    tempo_execucao = fim - inicio

    # Etapa 5: Relatório final
    print("\n" + "="*50)
    print("Relatório de Detecção de Falhas")
    print("="*50)
    print(f"Tipo de sinal com falha: {FAULT_TYPE}")
    print(f"Sinal injetado: {fault_signal}")
    print(f"Total de simulações: {NUM_SIMULATIONS}")
    print(f"Falhas detectadas: {detected_count}")
    print(f"Taxa de detecção: {detected_count/NUM_SIMULATIONS:.2%}")
    print(f"Tempo de execução: {tempo_execucao:.5f} segundos")
    
    # Código para salvar resultados em CSV (comentado)
    taxa_deteccao = detected_count / NUM_SIMULATIONS
    num_portas, num_entradas, num_saidas = simulator.get_infos()
    salvar_dados_csv(DESIGN_VERILOG, tempo_execucao, NUM_SIMULATIONS, num_entradas, num_saidas, taxa_deteccao, fault_signal, "data/resultados_simulacao_gates.csv")
    #gerar_tabela_csv("data/resultados_simulacao_gates.csv")

if __name__ == "__main__":
    main()
