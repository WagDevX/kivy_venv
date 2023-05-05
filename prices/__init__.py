
from kivymd.uix.list import OneLineRightIconListItem,IconRightWidget
from tarefas import show_snackbar

def add_prices(self, ean, qtd):
    try:
        if qtd == "":
            qtd = 1
        else:
            qtd = int(qtd)
        user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")

        # Verifica se o EAN já existe no Firebase
        ean_data = self.db.child("precos").child(ean).get(user['idToken']).val()

        if ean_data:
            # Atualiza a quantidade do EAN caso já exista
            ean_qtd = ean_data.get('Quantidade', 0)
            nova_qtd = ean_qtd + qtd
            data = {"Quantidade": nova_qtd}
            self.db.child("precos").child(ean).update(data, user['idToken'])
            for item in self.root.get_screen('main').ids.md_list.children:
                if isinstance(item, OneLineRightIconListItem) and getattr(item, 'ean', None) == ean:
                    item.text = f"EAN: {ean}     QTD: {nova_qtd}"
                    return

        else:
            # Cria um novo item caso o EAN não exista
            data = {"Quantidade": qtd}
            self.db.child("precos").child(ean).set(data, user['idToken'])

            item = OneLineRightIconListItem(
                IconRightWidget(
                    id=f"item_{ean}",
                    icon="delete-circle-outline",
                    on_press=lambda widget: self.delete_item(ean, item)
                ),
                text=f"EAN: {ean}     QTD: {qtd}"
            )
            self.root.get_screen('main').ids.md_list.add_widget(item)
            item.ean = ean
            show_snackbar("Adicionado com sucesso")
    except Exception:
        show_snackbar("Erro ao adicionar")

def add_all_items_from_firebase(self):
    try:
        for item in list(self.root.get_screen('main').ids.md_list.children):
            self.root.get_screen('main').ids.md_list.remove_widget(item)
        user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")
        all_items = self.db.child("precos").get(user['idToken'])
        for ean, data in all_items.val().items():
            qtd = data.get("Quantidade")
            item = OneLineRightIconListItem(
                IconRightWidget(
                    id=f"item_{ean}",
                    icon="delete-circle-outline",
                    on_press=lambda widget: self.delete_item(ean, item)
                ),
                text=f"EAN {ean}     QTD: {qtd}"
            )
            self.root.get_screen('main').ids.md_list.add_widget(item)
            item.ean = ean    
    except Exception:
            pass
        
def delete_item(self, ean, item):
    try:
        user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")
        self.db.child("precos").child(ean).remove(user['idToken'])
        self.root.get_screen('main').ids.md_list.remove_widget(item)
    except Exception:
        pass

