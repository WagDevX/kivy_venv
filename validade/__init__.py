
import pyrebase
import datetime
from tarefas import show_snackbar
import os
import ezodf
from kivy.utils import platform
if platform =='android':
    from jnius import autoclass

from firebase import db, id_token

def envia_validade_firebase(cod, desc, curva, qtd, vencimento, resp, setor):
        agora = datetime.datetime.now()
        agora_sem_milissegundos = agora.strftime("%d/%m/%y %H:%M")
        try:
            data = {"COD": cod,
                    "Descricao": desc,
                    "Curva": curva,
                    "QTD": qtd,
                    "Data_vencimento": vencimento,
                    "Responsável": resp,
                    "Data_de_adição": agora_sem_milissegundos
                    }
            db.child(setor).child("validade").push(data, id_token)
        except Exception:
            texto = "Erro ao exportar validade!"
            show_snackbar(texto)
        else:
            texto = "Exportado com sucesso!"
            show_snackbar(texto)
            return True
def adiciona_validade_da_busca(self, cod, desc):
     self.root.get_screen('fazer_validade').ids.ean_ou_in.text = cod
     self.root.get_screen('fazer_validade').ids.val_desc.text = desc
     self.root.current = 'fazer_validade'



def save_to_openoffice(data_table, index):
    # Criar um novo documento ODS
    doc = ezodf.newdoc(doctype='ods')


    # Adicionar uma planilha vazia
    sheet = ezodf.Sheet('Validade', size = (index, 8))
    doc.sheets.append(sheet)

    # Escrever cabeçalho
    headers = data_table.column_data
    for col, header in enumerate(headers, 1):
        sheet[0, col-1].set_value(header[0])

    # Escrever dados
    row_data = data_table.row_data
    for row, data in enumerate(row_data, 1):
        for col, value in enumerate(data, 1):
            sheet[row, col-1].set_value(value)

    # Obter pasta de downloads do usuário
    if platform == 'android':
        from jnius import autoclass
        Environment = autoclass('android.os.Environment')
        downloads_folder = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
    else:
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

    # Salvar arquivo
    agora = datetime.datetime.now()
    agora_sem_milissegundos = agora.strftime("%d-%m-%y")
    filename = os.path.join(downloads_folder, f"Validade-{agora_sem_milissegundos}.ods")
    doc.saveas(str(filename))


    return filename


def get_node_key(cod, desc, curva, qtd, data_vencimento, responsavel, setor):
    try:
        # Recuperar  nó desejado com base nos dados fornecidos
        query = db.child(setor).child("validade").order_by_child("COD").equal_to(cod).get(id_token)
        for item in query.each():
            if item.val().get("Descricao") == desc and item.val().get("Curva") == curva and item.val().get("QTD") == qtd and item.val().get("Data_vencimento") == data_vencimento and item.val().get("Responsável") == responsavel:
                node_key = item.key()
                break
        else:
            print("Nó não encontrado")
            return
        return node_key
        # Atualizar os dados do nó
        '''novos_dados = {
            "Descricao": desc,
            "Curva": curva,
            "QTD": qtd,
            "Data_vencimento": data_vencimento,
            "Responsável": responsavel
        }
        db.child(setor).child("validade").child(node_key).update(novos_dados, user['idToken'])
        print("Dados atualizados com sucesso")'''

    except Exception as e:
        print("Ocorreu um erro ao pegar a key", e)

def edit_selected_row(cod, desc, curva, qtd, data_vencimento, setor, node_key):
    novos_dados = {
        "COD": cod,
        "Descricao": desc,
        "Curva": curva,
        "QTD": qtd,
        "Data_vencimento": data_vencimento
    }
    db.child(setor).child("validade").child(node_key).update(novos_dados, id_token)
    show_snackbar("Dados atualizados com sucesso")
    
def remove_selected_row_firebase(setor, key):
    db.child(setor).child("validade").child(key).remove(id_token)