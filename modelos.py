from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres', 'password': 'thom2016'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Produtos(BaseModel):
    codigo_interno = IntegerField(null=True)
    descricao = TextField(null=True)
    ean = BigIntegerField(null=True)
    quantidade = IntegerField(null=True)

    class Meta:
        table_name = 'produtos'
        primary_key = False

class TesteInvent(BaseModel):
    codigo_interno = CharField(null=True)
    descricao = CharField(null=True)
    ean = CharField(null=True)
    quantidade = CharField(null=True)

    class Meta:
        table_name = 'teste_invent'
        primary_key = False