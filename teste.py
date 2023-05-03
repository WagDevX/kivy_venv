import csv
import json

csv_file = 'DADOS PRODUTOS.csv'
json_file = 'seu_arquivo.json'

# Abre o arquivo CSV e cria um leitor CSV
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)

    # Cria um dicionário vazio
    data = {}

    # Loop através de cada linha do CSV
    for row in reader:
        # Obtem a chave e a descrição a partir da linha
        key = row[0]
        descricao = row[1]

        # Adiciona a chave e a descrição ao dicionário como um novo item
        data[key] = {'descricao': descricao}

# Salva o dicionário como JSON em um arquivo
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)