
from kivymd.uix.list import OneLineRightIconListItem,IconRightWidget
from tarefas import show_snackbar
from kivymd.uix.list import TwoLineAvatarIconListItem,OneLineRightIconListItem,IconLeftWidget

import barcode
from firebase import db, id_token

def is_valid_ean(ean):
    if len(ean) != 13:
        return False

    # Calcula o dígito verificador esperado
    check_digit = int(ean[-1])
    ean_digits = [int(digit) for digit in ean[:-1]]
    computed_check_digit = sum(ean_digits[::2]) + sum(ean_digits[1::2]) * 3
    computed_check_digit = (10 - (computed_check_digit % 10)) % 10

    # Verifica se o dígito verificador é igual ao esperado
    return check_digit == computed_check_digit



class CustomButton(IconLeftWidget):
    def __init__(self, **kwargs):
        self.ean = kwargs.pop('ean')
        super().__init__(**kwargs)

def add_abastecimento_firebase(self):
    try:
        for item in list(self.root.get_screen('main').ids.lista_abastecimento.children):
            self.root.get_screen('main').ids.lista_abastecimento.remove_widget(item)
        all_items = db.child(self.loja).child(self.setor).child("abastecimento").get(id_token)
        for ean, data in all_items.val().items():
            qtd = data.get("Quantidade")
            desc = data.get("Descrição")
            item = TwoLineAvatarIconListItem(
                CustomButton(
                    icon="delete-circle-outline",
                    ean=ean,
                    on_press=self.delete_item_abastecimento
                ),
                text=ean,
                secondary_text = f"[ {qtd} ] - {desc}",
                secondary_font_style = "Caption"
            )
            self.root.get_screen('main').ids.lista_abastecimento.add_widget(item)
            item.ean = ean    
    except Exception:
        pass


def abastecimento(self, ean, qtd, desc):
    try:
        if qtd == "":
            qtd = 1
        else:
            qtd = int(qtd)
        # Verifica se o EAN já existe no Firebase
        ean_data = db.child(self.loja).child(self.setor).child("abastecimento").child(ean).get(id_token).val()

        if ean_data:
            # Atualiza a quantidade do EAN caso já exista
            ean_qtd = ean_data.get('Quantidade', 0)
            nova_qtd = ean_qtd + qtd
            data = {"Quantidade": nova_qtd}
            db.child(self.loja).child(self.setor).child("abastecimento").child(ean).update(data, id_token)
        else:
            # Cria um novo item caso o EAN não exista
            data = {"Quantidade": qtd,
                    "Descrição": desc}
            db.child(self.loja).child(self.setor).child("abastecimento").child(ean).set(data, id_token)

        # Atualiza o widget do item correspondente
        for item in self.root.get_screen('main').ids.lista_abastecimento.children:
            if isinstance(item, TwoLineAvatarIconListItem) and getattr(item, 'ean', None) == ean:
                item.text = ean
                item.secondary_text = f"[ {nova_qtd} ] - {desc}" if ean_data else f"[ {qtd} ] - {desc}"
                break
        else:
            # Cria um novo widget para o item adicionado
            item = TwoLineAvatarIconListItem(
                CustomButton(
                    icon="delete-circle-outline",
                    ean=ean,
                    on_press=self.delete_item_abastecimento
                ),
                text=ean,
                secondary_text = f"[ {qtd} ] - {desc}",
                secondary_font_style = "Caption"
            )
            self.root.get_screen('main').ids.lista_abastecimento.add_widget(item)
            item.ean = ean    
            show_snackbar("Adicionado com sucesso")
    except Exception:
        show_snackbar("Erro ao adicionar")