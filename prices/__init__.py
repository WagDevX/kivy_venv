
from kivymd.uix.list import OneLineRightIconListItem,IconRightWidget
from tarefas import show_snackbar
from kivymd.uix.list import TwoLineAvatarIconListItem,OneLineRightIconListItem,IconLeftWidget


class CustomButton(IconLeftWidget):
    def __init__(self, **kwargs):
        self.ean = kwargs.pop('ean')
        super().__init__(**kwargs)

def add_abastecimento_firebase(self):
    try:
        for item in list(self.root.get_screen('main').ids.lista_abastecimento.children):
            self.root.get_screen('main').ids.lista_abastecimento.remove_widget(item)
        user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")
        all_items = self.db.child("abastecimento").get(user['idToken'])
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
                secondary_text = f"[ {qtd} ] - {desc}"
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
        user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")

        # Verifica se o EAN já existe no Firebase
        ean_data = self.db.child("abastecimento").child(ean).get(user['idToken']).val()

        if ean_data:
            # Atualiza a quantidade do EAN caso já exista
            ean_qtd = ean_data.get('Quantidade', 0)
            nova_qtd = ean_qtd + qtd
            data = {"Quantidade": nova_qtd}
            self.db.child("abastecimento").child(ean).update(data, user['idToken'])
        else:
            # Cria um novo item caso o EAN não exista
            data = {"Quantidade": qtd,
                    "Descrição": desc}
            self.db.child("abastecimento").child(ean).set(data, user['idToken'])

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
                secondary_text = f"[ {qtd} ] - {desc}"
            )
            self.root.get_screen('main').ids.lista_abastecimento.add_widget(item)
            item.ean = ean    
            show_snackbar("Adicionado com sucesso")
    except Exception:
        show_snackbar("Erro ao adicionar")