import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mysql.connector
from config.db_config import configuraciones
from db.base import BaseDeDatos

class MySQLBD(BaseDeDatos):
    def __init__(self):
        config = configuraciones["mysql"]
        self.conn = mysql.connector.connect(
        host=config["host"],
        user=config["usuario"],
        password=config["contrasena"],
        database=config["base_datos"]
    )

        self.cursor = self.conn.cursor()

    def conectar(self):
        print("Conectado a MySQL")

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
