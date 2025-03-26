import tkinter as tk
from tkinter import filedialog
import subprocess

def browse_design():
    filename = filedialog.askopenfilename(
        title="Selecione o arquivo .bench",
        filetypes=[("Bench files", "*.bench"), ("All Files", "*.*")]
    )
    if filename:
        design_entry.delete(0, tk.END)
        design_entry.insert(0, filename)

def browse_fault():
    filename = filedialog.askopenfilename(
        title="Selecione o Fault List (opcional)",
        filetypes=[("All Files", "*.*")]
    )
    if filename:
        fault_entry.delete(0, tk.END)
        fault_entry.insert(0, filename)

def browse_output_vector():
    filename = filedialog.asksaveasfilename(
        title="Selecione onde salvar o Output Vector",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if filename:
        output_vector_entry.delete(0, tk.END)
        output_vector_entry.insert(0, filename)

def browse_output_relatorio():
    filename = filedialog.asksaveasfilename(
        title="Selecione onde salvar o Relatório",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if filename:
        output_relatorio_entry.delete(0, tk.END)
        output_relatorio_entry.insert(0, filename)

def run_atalanta():
    # Executa o comando apenas se o FAN estiver selecionado
    if not op1.get():
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Opção FAN não selecionada. Atalanta não será executado.\n")
        output_text.config(state="disabled")
        return

    design_file = design_entry.get()
    fault_file = fault_entry.get()
    output_vector_file = output_vector_entry.get()
    output_relatorio_file = output_relatorio_entry.get()

    # Verifica se os arquivos obrigatórios foram selecionados
    if not design_file:
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Arquivo de Design (.bench) não selecionado!\n")
        output_text.config(state="disabled")
        return

    if not output_vector_file or not output_relatorio_file:
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Arquivos de Output Vector ou Relatório não foram selecionados!\n")
        output_text.config(state="disabled")
        return

    # Monta o comando, considerando que fault_list é opcional
    # Exemplo de comando: 
    # atalanta -t "/home/joseg/Documentos/ATPG/testes_verilog/output_vector.txt" -f {fault_file} /home/joseg/Documentos/ATPG/testes_verilog/s27.bench > home/joseg/Documentos/ATPG/testes_verilog/relatorio.txt

    cmd = f'atalanta {design_file}'
    print(cmd)
    if fault_file:
        cmd = f'atalanta -f {fault_file} {design_file} > {output_relatorio_file}'
    elif output_vector_file and output_relatorio_file:
        cmd = f'atalanta -t {output_vector_file} {design_file} > {output_relatorio_file}'
    else:
        cmd = f'atalanta -t {output_vector_file} -f {fault_file} {design_file} > {output_relatorio_file}'
    print(cmd)

    # Exibe o comando que será executado
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"Executando comando:\n{cmd}\n\n")
    output_text.config(state="disabled")

    try:
        # Executa o comando e captura a saída
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output_text.config(state="normal")
        output_text.insert(tk.END, "Saída:\n")
        output_text.insert(tk.END, process.stdout)
        if process.stderr:
            output_text.insert(tk.END, "\nErros:\n")
            output_text.insert(tk.END, process.stderr)
        output_text.config(state="disabled")
    except Exception as e:
        output_text.config(state="normal")
        output_text.insert(tk.END, f"Erro ao executar comando: {e}")
        output_text.config(state="disabled")

# Criação da janela principal
janela = tk.Tk()
janela.geometry("800x500")
janela.title("Atalanta ATPG - Interface")

# Linha 0 e 1: Arquivo Design (.bench)
tk.Label(janela, text="Design (.bench):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
design_entry = tk.Entry(janela, width=20)
design_entry.grid(row=1, column=0, padx=10, pady=5, sticky="w")
tk.Button(janela, text="Browse", command=browse_design).grid(row=1, column=1, padx=5, pady=5)

# Linha 2 e 3: Fault list (opcional)
tk.Label(janela, text="Fault list (opcional):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
fault_entry = tk.Entry(janela, width=20)
fault_entry.grid(row=3, column=0, padx=10, pady=5, sticky="w")
tk.Button(janela, text="Browse", command=browse_fault).grid(row=3, column=1, padx=5, pady=5)

# Linha 4 e 5: Output Vector
tk.Label(janela, text="Output Vector:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
output_vector_entry = tk.Entry(janela, width=20)
output_vector_entry.grid(row=5, column=0, padx=10, pady=5, sticky="w")
tk.Button(janela, text="Browse", command=browse_output_vector).grid(row=5, column=1, padx=5, pady=5)

# Linha 6 e 7: Output Relatório
tk.Label(janela, text="Output Relatório:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
output_relatorio_entry = tk.Entry(janela, width=20)
output_relatorio_entry.grid(row=7, column=0, padx=10, pady=5, sticky="w")
tk.Button(janela, text="Browse", command=browse_output_relatorio).grid(row=7, column=1, padx=5, pady=5)

# Linha 8 a 10: Checkboxes
op1 = tk.BooleanVar()  # FAN (usado para executar o atalanta)
op2 = tk.BooleanVar()
op3 = tk.BooleanVar()

tk.Checkbutton(janela, text="FAN", variable=op1).grid(row=8, column=0, padx=10, pady=5, sticky="w")
tk.Checkbutton(janela, text="Baysean", variable=op2).grid(row=9, column=0, padx=10, pady=5, sticky="w")
tk.Checkbutton(janela, text="Random", variable=op3).grid(row=10, column=0, padx=10, pady=5, sticky="w")

# Botão de RUN (usa place para posicionamento absoluto)
run = tk.Button(janela, text="RUN", width=10, height=2, command=run_atalanta)
run.place(x=678, y=440)

# Área de texto para exibir o output (modo somente leitura)
output_text = tk.Text(janela, height=20, width=60, state="disabled")
output_text.grid(row=0, column=2, rowspan=11, padx=5, pady=10)

janela.mainloop()
