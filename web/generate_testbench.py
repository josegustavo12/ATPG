from yosys_extractor import YosysExtractor
import random

# TODO
# Adicionar formas de gerar diversos vetores
# adicionar vetor de preload

class GenerateTB:
    def __init__(self, netlist):
        """
        Classe para gerar o testbench a partir da netlist extraída.
        netlist: dicionário contendo as informações extraídas (inputs, outputs, wires, module, gates).
        """
        self.input_ports = netlist.get("inputs", [])
        self.output_ports = netlist.get("outputs", [])
        self.wires = netlist.get("wires", [])
        self.module_name = netlist.get("module", None)
        self.gates = netlist.get("gates", [])

    def generate_random_vector(self, rng=None):
        """Gera um vetor de teste aleatório para as entradas extraídas."""
        if rng is None:
            rng = random.Random()
        return {inp: rng.choice([0, 1]) for inp in self.input_ports}

    def generate_random_vectors(self, count=1, seed=None):
        """Gera uma lista de vetores aleatórios."""
        rng = random.Random(seed)  # Se seed for None, o gerador é iniciado aleatoriamente
        return [self.generate_random_vector(rng) for _ in range(count)]
    
    def create_testbench(self, vectors, tb_filename, fault=False, fault_port=None, fault_value=None, clock=False):
        """
        Cria um testbench Verilog que instancia o design e aplica uma lista de vetores de teste.
        Cada vetor é um dicionário com os valores para as entradas.
        
        Se fault=True, injeta a falha no sinal fault_port em cada vetor, forçando o mesmo valor:
        - Se fault_port é uma porta de entrada: força o valor oposto.
        - Se fault_port é uma porta de saída: usa 'force' para fixar o valor a 0.
        - Se fault_port é uma porta de gate (ex.: AND3_0): força a porta de saída (assumindo "Y")
            a 0 ou 1 dependendo do valor dentro de fault_value.
        - Se fault_port não é declarado externamente, assume-se que é um net interno e usa
            referência hierárquica (ex.: uut.<fault.port>).
        """
        tb_lines = []
        tb_lines.append("`timescale 1ns/1ps")
        tb_lines.append("module tb;")
        tb_lines.append("")
        
        # Declara as entradas e saídas com base na netlist extraída
        for inp in self.input_ports:
            tb_lines.append(f"  reg {inp};")
        for out in self.output_ports:
            tb_lines.append(f"  wire {out};")
        tb_lines.append("")
        
        # Instancia o design; assume que o nome do módulo é self.module_name
        conns = ", ".join([f".{p}({p})" for p in (self.input_ports + self.output_ports)])
        tb_lines.append(f"  {self.module_name} uut ({conns});")
        
        if clock:
            tb_lines.append("  // Geração do clock se necessário")
            tb_lines.append("  initial begin")
            tb_lines.append(f"     {self.input_ports[0]} = 0;")
            tb_lines.append(f"     forever #5 {self.input_ports[0]} = ~{self.input_ports[0]};")
            tb_lines.append("  end")
            tb_lines.append("")
        
        # Se fault=True, define o fault_port de forma única para todos os vetores
        fault_selection_comment = ""
        if fault:
            if not fault_port or fault_port.strip() == "":
                if self.wires:
                    fault_port = random.choice(self.wires)
                    fault_selection_comment = f"    // Falha solicitada sem porta definida; selecionado aleatoriamente '{fault_port}'"
                else:
                    fault_selection_comment = "    // Falha solicitada, mas nenhum wire disponível; nenhuma injeção realizada."
        
        tb_lines.append("  initial begin")
        # Itera sobre cada vetor da lista
        for idx, vector in enumerate(vectors):
            tb_lines.append(f"    // Aplicando vetor {idx+1}")
            # Atribuição dos valores de entrada para este vetor
            for inp in self.input_ports:
                tb_lines.append(f"    {inp} = {vector[inp]};")
            tb_lines.append("")
            
            # Injeção de falha em cada vetor se fault=True
            if fault:
                tb_lines.append("    #5;")
                if fault_selection_comment:
                    tb_lines.append(fault_selection_comment)
                if fault_port in self.wires:
                    value_str = "1" if fault_value else "0"
                    tb_lines.append(f"    force uut.{fault_port} = {value_str};  // Injetando falha: stuck-at {value_str} em {fault_port}")
                else:
                    tb_lines.append(f"    // O sinal '{fault_port}' não está entre os wires; nenhuma injeção realizada.")
            tb_lines.append("    #10;")
            
            # Imprime as saídas usando $display com o índice do vetor
            for out in self.output_ports:
                tb_lines.append(f'    $display("{idx+1}. OUTPUT: {out} = %b", {out});')
            tb_lines.append("")
        
        tb_lines.append("    $finish;")
        tb_lines.append("  end")
        tb_lines.append("endmodule")
        
        with open(tb_filename, "w") as f:
            f.write("\n".join(tb_lines))
        print(f"Testbench gerado em {tb_filename}")
