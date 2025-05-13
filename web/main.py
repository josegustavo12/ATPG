import json
from yosys_extractor import YosysExtractor
from simulador import Simulador
from generate_testbench import GenerateTB

def main():
    # Arquivo Verilog do design
    design_file = "c499.v"
    modulo_file = ""
    # Etapa 1: Extração com Yosys
    extractor = YosysExtractor()
    try:
        yosys_json = extractor.createjson(design_file)
        netlist = extractor.extract(yosys_json)
        print("Netlist extraída:")
        print(json.dumps(netlist, indent=4))
    except Exception as e:
        print("Erro durante a extração:", e)
        return
    
    # Etapa 2: Geração do Testbench
    # Gera um vetor de teste aleatório
    tb_gen = GenerateTB(netlist)
    test_vector = tb_gen.generate_random_vector()
    test_vectors = tb_gen.generate_random_vectors(count=10)
    print("Vetor de teste gerado:")
    print(test_vector)

    
    # Etapa 3: Simulação com ModelSim
    simulador = Simulador(netlist)
    sim_results = simulador.simulate(modulo_file, design_file, vector=test_vectors, clock=False, numero_falhas=100, fault_value=True)
    if sim_results is None:
        print("Simulação falhou.")
    else:
        print("Vetor de teste gerado:")
        print(test_vector)
        print("Resultados da Simulação:")
        print(sim_results)
    
    analysis = simulador.analyze_atpg_results(sim_results)
    print("Análise dos resultados:")
    for key, value in analysis.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()