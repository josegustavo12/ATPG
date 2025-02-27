#!/usr/bin/env python3
"""
main.py (Modificado)

Fluxo simplificado para 1000 simulações:
  1. Extrai a estrutura do design Verilog (arquivo fixo 'design.v').
  2. Inicializa o simulador combinacional.
  3. Executa 1000 simulações com vetores aleatórios diferentes.
  4. Mantém a falha fixa na porta especificada.
  5. Calcula e exibe estatísticas de detecção.
"""

import json
from simulacao.pyverilog_extractor import VerilogExtractor
from simulacao.simulator import CombinationalSimulator
from utils.data_utils import *
import time as t

def main():
    # Configurações fixas
    DESIGN_VERILOG = "verilog/c6288.v"
    FAULT_PORT = "G6"  # Porta fixa para injeção de falha
    NUM_SIMULATIONS = 1000

    # Etapa 1: Extração da netlist
    print("Extraindo estrutura do design...")
    extractor = VerilogExtractor()
    try:
        netlist = extractor.extract(DESIGN_VERILOG)
        extractor.save_json("simulacao/data/netlist.json")
    except Exception as e:
        print(f"Erro na extração: {e}")
        return

    # Etapa 2: Inicialização do simulador
    try:
        simulator = CombinationalSimulator(netlist)
    except Exception as e:
        print(f"Erro na inicialização do simulador: {e}")
        return

    # Etapa 3: Execução das simulações
    print(f"\nIniciando {NUM_SIMULATIONS} simulações com falha em '{FAULT_PORT}'...")
    detected_count = 0
    inicio = t.time()
    for i in range(NUM_SIMULATIONS):
    
        # Gera vetor de teste
        test_vector = simulator.generate_random_vector()
        
        # Simulação normal
        good_result = simulator.simulate(
            DESIGN_VERILOG,
            test_vector,
            fault=False
        )
        
        # Simulação com falha
        fault_result = simulator.simulate(
            DESIGN_VERILOG,
            test_vector,
            fault=True,
            fault_port=FAULT_PORT
        )

        # Comparação de resultados
        if good_result and fault_result and good_result != fault_result:
            detected_count += 1

        # Progresso a cada 10%
        if (i+1) % (NUM_SIMULATIONS//10) == 0:
            print(f"Progresso: {i+1}/{NUM_SIMULATIONS} simulações")
    fim = t.time()
    tempo_execucao = fim - inicio

    # Etapa 4: Relatório final
    print("\n" + "="*50)
    print("Relatório de Detecção de Falhas")
    print("="*50)
    print(f"Porta com falha: {FAULT_PORT}")
    print(f"Total de simulações: {NUM_SIMULATIONS}")
    print(f"Falhas detectadas: {detected_count}")
    print(f"Taxa de detecção: {detected_count/NUM_SIMULATIONS:.2%}")
    print(f"Tempo de execução: {tempo_execucao:.5}")
    
    # salvar no csv
    # nome_arquivo, tempo_execucao, num_portas, num_entradas_saidas, taxa_deteccao
    taxa_deteccao = detected_count/NUM_SIMULATIONS
    num_portas, num_entradas, num_saidas = simulator.get_infos()
    salvar_dados_csv(DESIGN_VERILOG, tempo_execucao, NUM_SIMULATIONS, num_entradas, num_saidas, taxa_deteccao, FAULT_PORT)
    gerar_tabela_csv("data/resultados_simulacao.csv")
    

if __name__ == "__main__":
    main()