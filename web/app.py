from flask import Flask, render_template, request, redirect, url_for, flash
import os
from yosys_extractor import YosysExtractor
from simulador import Simulador
from generate_testbench import GenerateTB

app = Flask(__name__)
app.secret_key = ""  # necessário para usar flash messages

# Lista de designs disponíveis (nome: descrição)
DESIGNS = {
    "c17": "Full adder",
    "c432": "27-channel interrupt controller",
    "c499": "32-bit SEC circuit",        # ou c1355 se preferir, ajuste conforme necessário
    "c880": "8-bit ALU",
    "c1908": "16-bit SEC/DED circuit",
    "c2670": "12-bit ALU and controller",
    "c3540": "8-bit ALU",
    "c5315": "9-bit ALU",
    "c6288": "16x16 multiplier",
    "c7552": "32-bit adder/comparator"
}

@app.route('/')
def index():
    return render_template('index.html', designs=DESIGNS)

@app.route('/simulate', methods=['POST'])
def simulate():
    # Recupera o design selecionado no formulário
    selected_design = request.form.get('design')
    if not selected_design:
        flash("Selecione um design!")
        return redirect(url_for('index'))
    
    # Define os caminhos dos arquivos a partir do design escolhido
    design_path = os.path.join("Benchmarks", "ISCAS85", selected_design, f"{selected_design}.v")
    module_path = design_path  # Supondo que os módulos e o design estão no mesmo arquivo

    # Recupera parâmetros do formulário
    num_vectors = int(request.form.get('num_vectors', 5))
    num_faults = int(request.form.get('num_faults', 1))
    
    # Etapa 1: Extração com Yosys
    extractor = YosysExtractor()
    try:
        yosys_json = extractor.createjson(design_path)
        netlist = extractor.extract(yosys_json)
    except Exception as e:
        flash(f"Erro na extração: {e}")
        return redirect(url_for('index'))
    
    # Etapa 2: Geração do Testbench e dos vetores de teste
    tb_gen = GenerateTB(netlist)
    test_vectors = tb_gen.generate_random_vectors(count=num_vectors)
    
    # Etapa 3: Simulação (com ou sem múltiplas injeções de falha)
    simulador = Simulador(netlist)
    sim_results = simulador.simulate(module_path, design_path, vector=test_vectors,
                                     clock=False, numero_falhas=num_faults, fault_value=True)
    
    if sim_results is None:
        flash("Simulação falhou.")
        return redirect(url_for('index'))
    
    # Integra a análise dos resultados usando a função analyze_atpg_results
    analysis = simulador.analyze_atpg_results(sim_results)
    
    return render_template('results.html',
                           design=selected_design,
                           description=DESIGNS.get(selected_design, ""),
                           netlist=netlist,
                           test_vectors=test_vectors,
                           sim_results=sim_results,
                           analysis=analysis,
                           num_vectors=num_vectors,
                           num_faults=num_faults)

if __name__ == '__main__':
    app.run(debug=True)
