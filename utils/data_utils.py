import csv
import os
from tabulate import tabulate

def salvar_dados_csv(nome_arquivo, tempo_execucao, num_simulacoes, num_entradas, num_saidas, taxa_deteccao, porta_perturbada, arquivo_saida="data/resultados_simulacao.csv"):
    headers = ["Nome do arquivo", "Tempo de Execução", "Número de simulações", "Número de Entradas", "Número de Saidas", "Taxa de Detecção", "Gate/Wire perturbada"]
    nome_tabela = nome_arquivo.replace("verilog/", "")
    row = [nome_tabela, f"{tempo_execucao:.5f}", num_simulacoes, num_entradas, num_saidas, f"{100*taxa_deteccao:.2f}%", porta_perturbada]

    os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)

    if os.path.exists(arquivo_saida):
        with open(arquivo_saida, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)
            found = any(r[0] == nome_tabela for r in rows[1:])
        if found:
            print(f"Design {nome_tabela} já existe no CSV. Não adicionando nova linha.")
            return
        else:
            with open(arquivo_saida, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(row)
            print(f"Nova linha adicionada para design {nome_tabela}.")
    else:
        with open(arquivo_saida, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerow(row)
        print(f"Arquivo CSV criado e dados adicionados para design {nome_tabela}.")
def gerar_tabela_csv(arquivo_csv, output_image="tabela.png"):
    import pandas as pd
    import matplotlib.pyplot as plt

    try:
        df = pd.read_csv(arquivo_csv)
    except Exception as e:
        print(f"Erro ao ler o CSV com pandas: {e}")
        return

    desc_row = [
        "Circuito", 
        "Tempo em s", 
        "Simulações realizadas", 
        "Entradas", 
        "Saídas", 
        "Detecção (%)", 
        "Sinal perturbado"
    ]

    headers = list(df.columns)
    data_rows = df.values.tolist()

    table_data = [desc_row, headers] + data_rows

    fig, ax = plt.subplots(figsize=(max(8, len(headers)*2), 0.5*len(table_data)+1))
    ax.axis('tight')
    ax.axis('off')

    table = ax.table(cellText=table_data, loc="center", cellLoc='center', edges='closed')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    plt.savefig(output_image, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Imagem da tabela salva em {output_image}")
