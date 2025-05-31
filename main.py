import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from db.mysql_DB import MySQLBD
from db.oracle_DB import OracleBD
from db.sqlServer_DB import SQLServerBD
import subprocess

SEDE_OPTIONS = {
    'Sede Retalhuleu': MySQLBD,
    'Sede Quetzaltenango': OracleBD,
    'Sede Mazatenango': SQLServerBD
}
ENTIDADES = ['Estudiante', 'Profesor', 'Curso']

CAMPOS = {
    'Estudiante': [('nombre', 'Nombre'), ('email', 'Email')],
    'Profesor': [('nombre', 'Nombre'), ('especialidad', 'Especialidad'), ('email', 'Email')],
    'Curso': [('nombre', 'Nombre'), ('descripcion', 'Descripción'), ('id_profesor', 'ID Profesor')]
}

ID_CAMPOS = {
    'Estudiante': 'id_estudiante',
    'Profesor': 'id_profesor',
    'Curso': 'id_curso'
}

# Paleta de colores
BG_COLOR = '#1565c0'  # Azul institucional
FG_COLOR = '#ffffff'  # Blanco
BTN_COLOR = '#42a5f5' # Azul claro
BTN_HOVER = '#1976d2' # Azul más oscuro
ENTRY_BG = '#e3f2fd'  # Azul muy claro
RESULT_BG = '#f5f5f5' # Gris claro

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Administración de Sedes")
        self.geometry("800x600")
        self.resizable(False, False)
        self.db_instance = None
        self.configure(bg=BG_COLOR)
        self.create_widgets()

    def create_widgets(self):
        # Encabezado
        header = tk.Label(self, text="Sistema de Administración de Sedes", font=("Arial", 18, "bold"), bg=BG_COLOR, fg=FG_COLOR, pady=10)
        header.pack(fill=tk.X)
        subheader = tk.Label(self, text="Universidad Mariano Gálvez de Guatemala", font=("Arial", 13, "italic"), bg=BG_COLOR, fg=FG_COLOR, pady=5)
        subheader.pack(fill=tk.X)

        # Selección de sede
        frame_top = tk.Frame(self, bg=BG_COLOR)
        frame_top.pack(pady=10)
        tk.Label(frame_top, text="Seleccionar sede:", bg=BG_COLOR, fg=FG_COLOR, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.sede_var = tk.StringVar(value=list(SEDE_OPTIONS.keys())[0])
        self.sede_combo = ttk.Combobox(frame_top, textvariable=self.sede_var, values=list(SEDE_OPTIONS.keys()), state="readonly", width=20, font=("Arial", 11))
        self.sede_combo.pack(side=tk.LEFT, padx=5)
        self.sede_combo.bind('<<ComboboxSelected>>', self.change_sede)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground=ENTRY_BG, background=ENTRY_BG)
        tk.Button(frame_top, text="Conectar", command=self.connect_db, bg=BTN_COLOR, fg=FG_COLOR, font=("Arial", 11, "bold"), activebackground=BTN_HOVER, activeforeground=FG_COLOR, bd=0, padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=10)

        # Selección de entidad
        frame_entidad = tk.Frame(self, bg=BG_COLOR)
        frame_entidad.pack(pady=10)
        tk.Label(frame_entidad, text="Entidad:", bg=BG_COLOR, fg=FG_COLOR, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.entidad_var = tk.StringVar(value=ENTIDADES[0])
        self.entidad_combo = ttk.Combobox(frame_entidad, textvariable=self.entidad_var, values=ENTIDADES, state="readonly", width=15, font=("Arial", 11))
        self.entidad_combo.pack(side=tk.LEFT, padx=5)

        # Operaciones CRUD
        frame_crud = tk.Frame(self, bg=BG_COLOR)
        frame_crud.pack(pady=10)
        for text, cmd in zip(["Insertar", "Consultar", "Actualizar", "Eliminar"], [self.insertar, self.consultar, self.actualizar, self.eliminar]):
            b = tk.Button(frame_crud, text=text, width=12, command=cmd, bg=BTN_COLOR, fg=FG_COLOR, font=("Arial", 11, "bold"), activebackground=BTN_HOVER, activeforeground=FG_COLOR, bd=0, padx=10, pady=5, cursor="hand2")
            b.pack(side=tk.LEFT, padx=8)

        # Backup y Restore
        frame_backup = tk.Frame(self, bg=BG_COLOR)
        frame_backup.pack(pady=10)
        for text, cmd in zip(["Backup", "Restaurar"], [self.backup_db, self.restore_db]):
            b = tk.Button(frame_backup, text=text, width=12, command=cmd, bg="#43a047", fg=FG_COLOR, font=("Arial", 11, "bold"), activebackground="#2e7031", activeforeground=FG_COLOR, bd=0, padx=10, pady=5, cursor="hand2")
            b.pack(side=tk.LEFT, padx=8)

        # Área de resultados
        result_frame = tk.Frame(self, bg=BG_COLOR)
        result_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        tk.Label(result_frame, text="Resultados / Mensajes:", bg=BG_COLOR, fg=FG_COLOR, font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        self.result_area = scrolledtext.ScrolledText(result_frame, width=95, height=18, state='disabled', bg=RESULT_BG, fg="#222", font=("Consolas", 11), bd=2, relief=tk.GROOVE)
        self.result_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def change_sede(self, event=None):
        self.db_instance = None
        self.log("Sede cambiada. Debe conectar nuevamente.")

    def connect_db(self):
        sede = self.sede_var.get()
        db_class = SEDE_OPTIONS[sede]
        try:
            self.db_instance = db_class()
            self.db_instance.conectar()
            self.log(f"Conectado a {sede}.")
        except Exception as e:
            self.db_instance = None
            self.log(f"Error al conectar a {sede}: {e}")
            messagebox.showerror("Error de conexión", str(e))

    def insertar(self):
        if not self.db_instance:
            self.log("Debe conectar primero a una sede.")
            return
        entidad = self.entidad_var.get()
        campos = CAMPOS[entidad]
        values = {}
        form = tk.Toplevel(self)
        form.title(f"Insertar {entidad}")
        form.configure(bg=BG_COLOR)
        entries = {}
        for i, (campo, label) in enumerate(campos):
            tk.Label(form, text=label+':', bg=BG_COLOR, fg=FG_COLOR, font=("Arial", 11)).grid(row=i, column=0, sticky='e', padx=8, pady=6)
            entry = tk.Entry(form, width=30, bg=ENTRY_BG, font=("Arial", 11))
            entry.grid(row=i, column=1, padx=8, pady=6)
            entries[campo] = entry
        def submit():
            for campo, entry in entries.items():
                values[campo] = entry.get()
            try:
                query, params = self.get_insert_query(entidad, values)
                self.db_instance.insertar(query, params)
                self.log(f"{entidad} insertado correctamente.")
                form.destroy()
            except Exception as e:
                self.log(f"Error al insertar {entidad}: {e}")
        tk.Button(form, text="Insertar", command=submit, bg=BTN_COLOR, fg=FG_COLOR, font=("Arial", 11, "bold"), activebackground=BTN_HOVER, activeforeground=FG_COLOR, bd=0, padx=10, pady=5, cursor="hand2").grid(row=len(campos), column=0, columnspan=2, pady=10)

    def consultar(self):
        if not self.db_instance:
            self.log("Debe conectar primero a una sede.")
            return
        entidad = self.entidad_var.get()
        table_name = entidad  # Usar el nombre exacto
        try:
            query = f"SELECT * FROM {table_name}"
            self.log(f"Ejecutando query: {query}")
            resultados = self.db_instance.consultar(query)
            self.log(f"Resultados de {entidad}:")
            if not resultados:
                self.log("(Sin resultados)")
            else:
                # Mostrar nombres de columnas
                colnames = [desc[0] for desc in self.db_instance.cursor.description]
                self.log(' | '.join(colnames))
            for fila in resultados:
                self.log(' | '.join(str(x) for x in fila))
        except Exception as e:
            self.log(f"Error al consultar {entidad}: {e}")

    def actualizar(self):
        if not self.db_instance:
            self.log("Debe conectar primero a una sede.")
            return
        entidad = self.entidad_var.get()
        campos = CAMPOS[entidad]
        id_campo = ID_CAMPOS[entidad]
        form = tk.Toplevel(self)
        form.title(f"Actualizar {entidad}")
        form.configure(bg=BG_COLOR)
        tk.Label(form, text=f"{id_campo} a actualizar:", bg=BG_COLOR, fg=FG_COLOR, font=("Arial", 11)).grid(row=0, column=0, sticky='e', padx=8, pady=6)
        id_entry = tk.Entry(form, width=15, bg=ENTRY_BG, font=("Arial", 11))
        id_entry.grid(row=0, column=1, padx=8, pady=6)
        entries = {}
        for i, (campo, label) in enumerate(campos):
            tk.Label(form, text=label+':', bg=BG_COLOR, fg=FG_COLOR, font=("Arial", 11)).grid(row=i+1, column=0, sticky='e', padx=8, pady=6)
            entry = tk.Entry(form, width=30, bg=ENTRY_BG, font=("Arial", 11))
            entry.grid(row=i+1, column=1, padx=8, pady=6)
            entries[campo] = entry
        def submit():
            id_val = id_entry.get()
            values = {campo: entry.get() for campo, entry in entries.items()}
            try:
                query, params = self.get_update_query(entidad, id_campo, id_val, values)
                self.db_instance.actualizar(query, params)
                self.log(f"{entidad} actualizado correctamente.")
                form.destroy()
            except Exception as e:
                self.log(f"Error al actualizar {entidad}: {e}")
        tk.Button(form, text="Actualizar", command=submit, bg=BTN_COLOR, fg=FG_COLOR, font=("Arial", 11, "bold"), activebackground=BTN_HOVER, activeforeground=FG_COLOR, bd=0, padx=10, pady=5, cursor="hand2").grid(row=len(campos)+1, column=0, columnspan=2, pady=10)

    def eliminar(self):
        if not self.db_instance:
            self.log("Debe conectar primero a una sede.")
            return
        entidad = self.entidad_var.get()
        id_campo = ID_CAMPOS[entidad]
        form = tk.Toplevel(self)
        form.title(f"Eliminar {entidad}")
        form.configure(bg=BG_COLOR)
        tk.Label(form, text=f"{id_campo} a eliminar:", bg=BG_COLOR, fg=FG_COLOR, font=("Arial", 11)).grid(row=0, column=0, sticky='e', padx=8, pady=6)
        id_entry = tk.Entry(form, width=15, bg=ENTRY_BG, font=("Arial", 11))
        id_entry.grid(row=0, column=1, padx=8, pady=6)
        def submit():
            id_val = id_entry.get()
            try:
                query, params = self.get_delete_query(entidad, id_campo, id_val)
                self.db_instance.eliminar(query, params)
                self.log(f"{entidad} eliminado correctamente.")
                form.destroy()
            except Exception as e:
                self.log(f"Error al eliminar {entidad}: {e}")
        tk.Button(form, text="Eliminar", command=submit, bg="#e53935", fg=FG_COLOR, font=("Arial", 11, "bold"), activebackground="#b71c1c", activeforeground=FG_COLOR, bd=0, padx=10, pady=5, cursor="hand2").grid(row=1, column=0, columnspan=2, pady=10)

    def get_insert_query(self, entidad, values):
        campos = ', '.join(values.keys())
        placeholders = ', '.join(['%s']*len(values))
        if isinstance(self.db_instance, OracleBD):
            placeholders = ', '.join([f':{i+1}' for i in range(len(values))])
        query = f"INSERT INTO {entidad} ({campos}) VALUES ({placeholders})"
        params = tuple(values.values())
        return query, params

    def get_update_query(self, entidad, id_campo, id_val, values):
        set_clause = ', '.join([f"{k}=%s" for k in values.keys()])
        if isinstance(self.db_instance, OracleBD):
            set_clause = ', '.join([f"{k}=:{i+1}" for i, k in enumerate(values.keys())])
        query = f"UPDATE {entidad} SET {set_clause} WHERE {id_campo}=%s"
        params = tuple(values.values()) + (id_val,)
        if isinstance(self.db_instance, OracleBD):
            params = tuple(values.values()) + (id_val,)
        return query, params

    def get_delete_query(self, entidad, id_campo, id_val):
        query = f"DELETE FROM {entidad} WHERE {id_campo}=%s"
        params = (id_val,)
        if isinstance(self.db_instance, OracleBD):
            query = f"DELETE FROM {entidad} WHERE {id_campo}=:1"
        return query, params

    def backup_db(self):
        sede = self.sede_var.get()
        if sede == 'Sede Retalhuleu':
            self.backup_mysql()
        elif sede == 'Sede Mazatenango':
            self.backup_sqlserver()
        elif sede == 'Sede Quetzaltenango':
            self.backup_oracle()
        else:
            self.log("Backup no implementado para esta sede.")

    def restore_db(self):
        sede = self.sede_var.get()
        if sede == 'Sede Retalhuleu':
            self.restore_mysql()
        elif sede == 'Sede Mazatenango':
            self.restore_sqlserver()
        elif sede == 'Sede Quetzaltenango':
            self.restore_oracle()
        else:
            self.log("Restauración no implementada para esta sede.")

    def backup_mysql(self):
        from config.db_config import configuraciones
        config = configuraciones['mysql']
        file_path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql")])
        if not file_path:
            return
        cmd = [
            'mysqldump',
            f"-h{config['host']}",
            f"-u{config['usuario']}",
            f"-p{config['contrasena']}",
            config['base_datos'],
            f"--result-file={file_path}"
        ]
        try:
            subprocess.run(cmd, check=True)
            self.log(f"Backup MySQL realizado en {file_path}")
        except Exception as e:
            self.log(f"Error en backup MySQL: {e}")

    def restore_mysql(self):
        from config.db_config import configuraciones
        config = configuraciones['mysql']
        file_path = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql")])
        if not file_path:
            return
        cmd = [
            'mysql',
            f"-h{config['host']}",
            f"-u{config['usuario']}",
            f"-p{config['contrasena']}",
            config['base_datos']
        ]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                subprocess.run(cmd, stdin=f, check=True)
            self.log(f"Restauración MySQL completada desde {file_path}")
        except Exception as e:
            self.log(f"Error en restauración MySQL: {e}")

    def backup_sqlserver(self):
        from config.db_config import configuraciones
        config = configuraciones['sqlserver']
        file_path = filedialog.asksaveasfilename(defaultextension=".bak", filetypes=[("Backup files", "*.bak")])
        if not file_path:
            return
        query = f"BACKUP DATABASE {config['base_datos']} TO DISK = '{file_path}'"
        try:
            import pyodbc
            conn = pyodbc.connect(
                f"DRIVER={config['driver']};SERVER={config['servidor']};DATABASE={config['base_datos']};UID={config['usuario']};PWD={config['contrasena']}"
            )
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            self.log(f"Backup SQL Server realizado en {file_path}")
        except Exception as e:
            self.log(f"Error en backup SQL Server: {e}")

    def restore_sqlserver(self):
        from config.db_config import configuraciones
        config = configuraciones['sqlserver']
        file_path = filedialog.askopenfilename(filetypes=[("Backup files", "*.bak")])
        if not file_path:
            return
        query = f"RESTORE DATABASE {config['base_datos']} FROM DISK = '{file_path}' WITH REPLACE"
        try:
            import pyodbc
            conn = pyodbc.connect(
                f"DRIVER={config['driver']};SERVER={config['servidor']};DATABASE=master;UID={config['usuario']};PWD={config['contrasena']}"
            )
            cursor = conn.cursor()
            cursor.execute(f"ALTER DATABASE {config['base_datos']} SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
            cursor.execute(query)
            cursor.execute(f"ALTER DATABASE {config['base_datos']} SET MULTI_USER")
            conn.commit()
            conn.close()
            self.log(f"Restauración SQL Server completada desde {file_path}")
        except Exception as e:
            self.log(f"Error en restauración SQL Server: {e}")

    def backup_oracle(self):
        from config.db_config import configuraciones
        config = configuraciones['oracle']
        file_path = filedialog.asksaveasfilename(defaultextension=".dmp", filetypes=[("Dump files", "*.dmp")])
        if not file_path:
            return
        user = config['usuario']
        pwd = config['contrasena']
        dsn = config['dsn']
        cmd = [
            'exp',
            f"{user}/{pwd}@{dsn}",
            f"file={file_path}",
            f"owner={user}"
        ]
        try:
            subprocess.run(cmd, check=True)
            self.log(f"Backup Oracle realizado en {file_path}")
        except Exception as e:
            self.log(f"Error en backup Oracle: {e}")

    def restore_oracle(self):
        from config.db_config import configuraciones
        config = configuraciones['oracle']
        file_path = filedialog.askopenfilename(filetypes=[("Dump files", "*.dmp")])
        if not file_path:
            return
        user = config['usuario']
        pwd = config['contrasena']
        dsn = config['dsn']
        cmd = [
            'imp',
            f"{user}/{pwd}@{dsn}",
            f"file={file_path}",
            f"full=y"
        ]
        try:
            subprocess.run(cmd, check=True)
            self.log(f"Restauración Oracle completada desde {file_path}")
        except Exception as e:
            self.log(f"Error en restauración Oracle: {e}")

    def log(self, msg):
        self.result_area.config(state='normal')
        self.result_area.insert(tk.END, msg + '\n')
        self.result_area.see(tk.END)
        self.result_area.config(state='disabled')

if __name__ == "__main__":
    app = App()
    app.mainloop()
