from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRaisedButton


class Example(MDApp):
    data_tables = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        layout = MDFloatLayout()
        layout.add_widget(
            MDRaisedButton(
                text="Change 2 row",
                pos_hint={"center_x": 0.5},
                on_release=self.update_row,
                y=24,
            )
        )
        self.data_tables = MDDataTable(
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            size_hint=(0.9, 0.6),
            use_pagination=False,
            column_data=[
                ("No.", dp(30)),
                ("Column 1", dp(40)),
                ("Column 2", dp(40)),
                ("Column 3", dp(40)),
            ],
            row_data=[(f"{i + 1}", "1", "2", "3") for i in range(3)],
        )
        layout.add_widget(self.data_tables)

        return layout

    def update_row(self, instance_button: MDRaisedButton) -> None:
        self.data_tables.update_row(
            self.data_tables.row_data[1],  # old row data
            ["2", "A", "B","C"],          # new row data
        )


Example().run()