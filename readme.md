
# Implementação em FPGA de uma Framework para Análise de Confiabilidade de Circuitos Combinacionais Usando Inferência Bayesiana Aproximada

**Autor:** José Gustavo Victor Pinheiro Alencar  
**Instituição:** ICMC-USP

---

## 1. Introdução

Este projeto tem como objetivo desenvolver uma framework que permita analisar a confiabilidade de circuitos combinacionais através da injeção de falhas (stuck‑at) e da geração automática de vetores de teste usando algoritmos de ATPG (como PODEM). Além disso, a framework integra a simulação dos circuitos via Icarus Verilog com a extração do design (netlist) utilizando o Pyverilog e possibilita a análise de confiabilidade por meio de inferência bayesiana aproximada. O fluxo também contempla a eventual implementação do design em FPGA para validação em hardware real.

---

## 2. Estrutura do Projeto

A estrutura de arquivos do projeto é organizada da seguinte forma:

- **pyverilog_extractor.py**: Módulo que utiliza o Pyverilog para extrair a AST do código Verilog e organiza as informações dos módulos, portas (inputs, outputs, inouts) e conexões em um dicionário. Pode salvar essa estrutura em um arquivo JSON para análises posteriores.
- **simulator.py**: Módulo que gera vetores de teste aleatórios (com opção de definir a seed) com base nas portas de entrada extraídas. Cria automaticamente um testbench Verilog (em dois modos: circuito “bom” e circuito com uma porta perturbada para simular uma falha), chama o Icarus Verilog via `subprocess` para compilar e simular o design e processa os resultados.
- **main.py**: Arquivo principal que integra o fluxo completo. Ele chama o extractor para gerar a netlist, inicializa o simulador combinacional, gera o vetor de teste, executa as simulações (sem e com falha) e compara os resultados para indicar se a falha foi detectada.

---

## 3. Funcionamento do Código

### 3.1 Extração do Design com Pyverilog

- **Objetivo:** Ler o arquivo Verilog e extrair a estrutura do circuito, identificando os módulos, bem como as portas de entrada e saída.  
- **Como funciona:**  
  - O módulo `pyverilog_extractor.py` utiliza a função `parse()` do Pyverilog para obter a AST do design.
  - Inicialmente, os nomes dos sinais são extraídos a partir da *portlist* do módulo.  
  - Em seguida, o código percorre as declarações (itens do tipo `Decl`) para identificar os sinais que são declarados como `Input`, `Output` ou `Inout` e registra essas informações (direção e largura) em um dicionário.
  - Por fim, a estrutura completa é armazenada no objeto `self.structure` e pode ser salva em JSON.

### 3.2 Simulação do Circuito com Icarus Verilog

- **Objetivo:** Simular o circuito combinacional utilizando o Icarus Verilog e testar a detecção de falhas.  
- **Fluxo de Simulação:**  
  1. **Geração de Vetores de Teste Aleatórios:**  
     - O módulo `simulator.py` gera um vetor de teste aleatório para as entradas extraídas automaticamente da netlist.
     - É possível definir uma *seed* para reprodutibilidade dos testes.
  2. **Criação Automática do Testbench:**  
     - O simulador gera dinamicamente um arquivo de testbench Verilog.  
     - No modo “bom”, o testbench aplica os valores gerados às entradas e imprime as saídas usando `$display`.
     - No modo “com falha”, após um pequeno delay, o testbench força uma porta específica (por exemplo, a porta “b”) a assumir o valor oposto ao definido inicialmente, simulando assim uma falha.
  3. **Compilação e Execução com Icarus Verilog:**  
     - O script utiliza `subprocess` para chamar `iverilog` (para compilar) e `vvp` (para executar a simulação).
     - A saída da simulação é capturada e processada, buscando linhas que comecem com `"OUTPUT:"`.
  4. **Comparação dos Resultados:**  
     - Os resultados obtidos na simulação do design “bom” e do design com a falha são comparados.  
     - Se as saídas diferirem, a falha foi detectada.

## 4. Tecnologias Utilizadas

- **Python 3:** Linguagem principal para desenvolvimento do fluxo.
- **Pyverilog:** Toolkit para parsing e análise de códigos Verilog.
- **Icarus Verilog:** Simulador open-source para compilação e execução de designs Verilog.
- **Subprocess (Python):** Módulo para chamar comandos de linha de comando (usado para integrar o Icarus Verilog).
- **JSON:** Formato para salvar e manipular a estrutura extraída do design.

## 5. Testes realizados
![Tabela de Simulação](data/tabela_simulacao.png)


---

## Fontes e Artigos Utilizados

1. **Pyverilog: A Python-Based Hardware Design Processing Toolkit for Verilog HDL**  
   *Shinya Takamaeda-Yamazaki (2015).*  
   Apresenta a ferramenta Pyverilog e suas aplicações na análise de designs Verilog.  
   [Springer DOI](https://doi.org/10.1007/978-3-319-16214-0_42)

2. **Icarus Verilog: Open-Source Verilog More Than a Year Later**  
   *Stephen Williams e Michael Baxter (2002).*  
   Descrição do simulador Icarus Verilog e suas funcionalidades.  
   [Linux Journal](https://www.linuxjournal.com/article/6001)

3. **Diagnosis of Automata Failures: A Calculus and a Method**  
   *J. P. Roth (1966).*  
   Artigo seminal que introduziu o D-Algorithm para geração de testes.  
   [Semantic Scholar](https://www.semanticscholar.org/paper/Diagnosis-of-automata-failures%3A-a-calculus-and-a-Roth/)

4. **An Implicit Enumeration Algorithm to Generate Tests for Combinational Logic Circuits**  
   *Prabhu Goel (1981).*  
   Apresenta o algoritmo PODEM para geração de testes para circuitos digitais.  
   [IEEE Xplore](https://ieeexplore.ieee.org/document/1675757)

5. **On the Acceleration of Test Generation Algorithms**  
   *Hideo Fujiwara e Takeshi Shimono (1983).*  
   Discussão sobre o algoritmo FAN para geração de testes e melhorias de desempenho.  
   [IEEE Xplore](https://ieeexplore.ieee.org/document/1676133)

6. **Simulated Fault Injection Using Simulator Modification Technique**  
   *Jongwhoa Na e Dongwoo Lee (2011).*  
   Técnica para simulação de injeção de falhas em modelos Verilog.  
   [ETRI Journal](https://onlinelibrary.wiley.com/doi/10.4218/etrij.11.0110.0106)

7. **A Framework for Reliability Analysis of Combinational Circuits Using Approximate Bayesian Inference**  
   *Shivani Bathla e Vinita Vasudevan (2023).*  
   Aplica inferência bayesiana para estimar a confiabilidade de circuitos combinacionais.  
   [IEEE Xplore](https://ieeexplore.ieee.org/document/10026780)

8. **AutoBench: Automatic Testbench Generation and Evaluation Using LLMs for HDL Design**  
   *Ruidi Qiu et al. (2024).*  
   Aborda a geração automática de testbenches a partir de descrições de designs HDL.  
   [arXiv](https://arxiv.org/abs/2407.03891)

---

## 7. Livros Recomendados

### Eletrônica Digital e Verilog
- **Digital Design: With an Introduction to the Verilog HDL**  
  *M. Morris Mano & Michael D. Ciletti (5ª ed., 2013).*  
  Um dos livros mais clássicos para entender os fundamentos da eletrônica digital e a linguagem Verilog.

- **Digital Systems Testing and Testable Design**  
  *Miron Abramovici, Melvin A. Breuer & Arthur D. Friedman (1994).*  
  Aborda métodos de teste de sistemas digitais, incluindo algoritmos ATPG e conceitos de testabilidade.

- **Essentials of Electronic Testing for Digital, Memory and Mixed-Signal VLSI Circuits**  
  *Michael L. Bushnell & Vishwani D. Agrawal (2000).*  
  Guia completo sobre testes eletrônicos e técnicas para garantir a confiabilidade de circuitos VLSI.

### Testbench e Verificação de Hardware
- **Writing Testbenches: Functional Verification of HDL Models**  
  *Janick Bergeron (2ª ed., 2003).*  
  Guia prático para a criação de testbenches e verificação funcional de designs HDL, com foco em boas práticas de automação de testes.

- **Python for RTL Verification: A Complete Course in Python, cocotb, and pyuvm**  
  *Ray Salemi (2022).*  
  Livro que une Python e verificação RTL, mostrando como usar frameworks modernos para criar testbenches e automatizar a verificação de hardware.

### Confiabilidade e Inferência Bayesiana
- **Fault-Tolerant Systems**  
  *Israel Koren & C. Mani Krishna (2007).*  
  Aborda fundamentos de sistemas tolerantes a falhas e técnicas de confiabilidade aplicadas a sistemas digitais.

---

## 8. Conclusão

Este projeto integra diversas ferramentas e técnicas para a análise de confiabilidade de circuitos combinacionais. O fluxo desenvolvido envolve:

- **Extração automática** do design Verilog utilizando Pyverilog.
- **Geração de vetores de teste** aleatórios com reprodutibilidade (via seed).
- **Criação dinâmica de testbenches** para simulação com Icarus Verilog, permitindo a comparação entre a simulação do circuito correto e a simulação com uma falha injetada (perturbação em uma porta).
- **Processamento dos resultados** para verificar se a falha é detectada, permitindo, futuramente, integrar essa informação com métodos de inferência bayesiana para análise de confiabilidade.

As fontes e livros recomendados fornecem um embasamento teórico que vai desde os fundamentos da eletrônica digital e HDL até técnicas avançadas de testes e verificação, essenciais para quem deseja aprofundar no tema.

---

## 9. Licença

(Defina a licença do projeto, se aplicável.)

---

Este README foi elaborado para servir como parte de um relatório científico e fornecer uma visão completa e detalhada do funcionamento e dos fundamentos teóricos do projeto. Se houver dúvidas ou sugestões, por favor, entre em contato.

---

### Fontes e Referências Citadas

1. Takamaeda-Yamazaki, S. (2015). *Pyverilog: A Python-Based Hardware Design Processing Toolkit for Verilog HDL.* Springer. [DOI](https://doi.org/10.1007/978-3-319-16214-0_42)
2. Williams, S., & Baxter, M. (2002). *Icarus Verilog: Open-Source Verilog More Than a Year Later.* Linux Journal.
3. Roth, J. P. (1966). *Diagnosis of Automata Failures: A Calculus and a Method.* IBM Journal of R&D.
4. Goel, P. (1981). *An Implicit Enumeration Algorithm to Generate Tests for Combinational Logic Circuits.* IEEE.
5. Fujiwara, H., & Shimono, T. (1983). *On the Acceleration of Test Generation Algorithms.* IEEE Transactions on Computers.
6. Na, J., & Lee, D. (2011). *Simulated Fault Injection Using Simulator Modification Technique.* ETRI Journal.
7. Bathla, S., & Vasudevan, V. (2023). *A Framework for Reliability Analysis of Combinational Circuits Using Approximate Bayesian Inference.* IEEE Transactions on VLSI Systems.
8. Qiu, R. et al. (2024). *AutoBench: Automatic Testbench Generation and Evaluation Using LLMs for HDL Design.* arXiv preprint.

### Livros Recomendados

- **Digital Design: With an Introduction to the Verilog HDL** – M. Morris Mano & Michael D. Ciletti.
- **Digital Systems Testing and Testable Design** – Miron Abramovici, Melvin A. Breuer & Arthur D. Friedman.
- **Essentials of Electronic Testing for Digital, Memory and Mixed-Signal VLSI Circuits** – Michael L. Bushnell & Vishwani D. Agrawal.
- **Writing Testbenches: Functional Verification of HDL Models** – Janick Bergeron.
- **Python for RTL Verification: A Complete Course in Python, cocotb, and pyuvm** – Ray Salemi.
- **Fault-Tolerant Systems** – Israel Koren & C. Mani Krishna.

---

*José Gustavo Victor Pinheiro Alencar, ICMC-USP – 2025*