import pyodbc
from config.db_config import configuraciones
from db.base import BaseDeDatos

class SQLServerBD(BaseDeDatos):
    def __init__(self):
        config = configuraciones["sqlserver"]

        if config.get("autenticacion_windows", False):
            # Autenticación de Windows
            cadena = (
                f"DRIVER={config['driver']};"
                f"SERVER={config['servidor']};"
                f"DATABASE={config['base_datos']};"
                f"Trusted_Connection=yes;"
            )
        else:
            # Autenticación con usuario y contraseña
            cadena = (
                f"DRIVER={config['driver']};"
                f"SERVER={config['servidor']};"
                f"DATABASE={config['base_datos']};"
                f"UID={config['usuario']};"
                f"PWD={config['contrasena']};"
            )

        self.conn = pyodbc.connect(cadena)
        self.cursor = self.conn.cursor()

    def conectar(self):
        print("Conectado a SQL Server")

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
