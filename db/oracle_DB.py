import cx_Oracle
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import configuraciones
from db.base import BaseDeDatos

class OracleBD(BaseDeDatos):
    def __init__(self):
        config = configuraciones["oracle"]
        self.conn = cx_Oracle.connect(config["usuario"], config["contrasena"], config["dsn"])
        self.cursor = self.conn.cursor()

    def conectar(self):
        print("Conectado a Oracle")

    def insertar(self, query, params):
        self.cursor.execute(query, params)
        self.conn.commit()

    def consultar(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def actualizar(self, query, params):
        self.cursor.execute(query, params)
        self.conn.commit()

    def eliminar(self, query, params):
        self.cursor.execute(query, params)
        self.conn.commit()