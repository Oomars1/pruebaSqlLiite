import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


# Función para conectar a la base de datos
def connect_db():
    conn = sqlite3.connect('data.db')
    return conn

# Crear tablas si no existen
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Crear tabla 'codes'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS codes (
        code INTEGER PRIMARY KEY,
        threshold INTEGER
    )
    ''')

    # Crear tabla 'UMB'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UMB (
        umb TEXT PRIMARY KEY
    )
    ''')

    # Crear tabla 'umb_codes'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS umb_codes (
        umb TEXT,
        code INTEGER,
        FOREIGN KEY(umb) REFERENCES UMB(umb),
        FOREIGN KEY(code) REFERENCES codes(code),
        PRIMARY KEY(umb, code)
    )
    ''')

    conn.commit()
    conn.close()

# Función para cargar datos desde la base de datos
def load_data():
    conn = connect_db()
    cursor = conn.cursor()

    # Cargar códigos y umbrales
    cursor.execute('SELECT * FROM codes')
    codes = dict(cursor.fetchall())

    # Cargar UMBs
    cursor.execute('SELECT umb FROM UMB')
    umbs = {row[0]: [] for row in cursor.fetchall()}

    # Cargar códigos asociados a UMBs
    cursor.execute('SELECT umb, code FROM umb_codes')
    for umb, code in cursor.fetchall():
        if umb in umbs:
            umbs[umb].append(code)

    conn.close()
    return codes, umbs

# Crear las tablas en la base de datos
create_tables()

# Leer los datos de la base de datos
codes, UMB = load_data()

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Consulta de Códigos")
        self.geometry("800x600")

        # Entrada de código
        self.label = tk.Label(self, text="Seleccione el código:")
        self.label.pack(pady=10)

        # Menú desplegable para seleccionar código
        self.code_var = tk.StringVar()
        self.code_var.set(next(iter(codes.keys()), ''))  # Establecer un valor predeterminado

        self.code_dropdown = ttk.Combobox(self, textvariable=self.code_var, values=list(codes.keys()))
        self.code_dropdown.pack(pady=10)
        self.code_dropdown.bind("<<ComboboxSelected>>", self.show_info)

        # Botón para agregar código
        self.add_code_button = tk.Button(self, text="Agregar Código", command=self.add_code_window)
        self.add_code_button.pack(pady=10)

        # Área de texto para mostrar resultados
        self.text_area = scrolledtext.ScrolledText(self, width=50, height=15)
        self.text_area.pack(pady=10)

    def show_info(self, event=None):
        code = int(self.code_var.get())
        if code in codes:
            # Obtener el umbral
            threshold = codes[code]

            # Buscar el UMB correspondiente
            umb_prefix = None
            for key, value in UMB.items():
                if code in value:
                    umb_prefix = key
                    break

            umb_info = f"UMB: {umb_prefix}" if umb_prefix else "Información UMB no encontrada."
            
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"Código {code} tiene un umbral de {threshold}\n")
            self.text_area.insert(tk.END, f"Información UMB: {umb_info}\n")
        else:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"Código {code} no encontrado\n")

    def add_code_window(self):
        self.add_window = tk.Toplevel(self)
        self.add_window.title("Agregar Código")

        self.add_code_label = tk.Label(self.add_window, text="Código:")
        self.add_code_label.pack(pady=5)

        self.add_code_entry = tk.Entry(self.add_window)
        self.add_code_entry.pack(pady=5)

        self.add_umb_label = tk.Label(self.add_window, text="UMB:")
        self.add_umb_label.pack(pady=5)

        # Crear el menú desplegable para UMB
        self.add_umb_var = tk.StringVar()
        self.add_umb_var.set(next(iter(UMB.keys()), ''))  # Establecer un valor predeterminado

        self.umb_dropdown = ttk.Combobox(self.add_window, textvariable=self.add_umb_var, values=list(UMB.keys()))
        self.umb_dropdown.pack(pady=5)

        self.add_button = tk.Button(self.add_window, text="Agregar", command=self.add_code)
        self.add_button.pack(pady=10)

    def add_code(self):
        code = self.add_code_entry.get()
        umb = self.add_umb_var.get()

        if code.isdigit() and len(code) > 0:
            code = int(code)
            threshold = codes.get(code, 10)  # Usar umbral predeterminado si no se encuentra

            conn = connect_db()
            cursor = conn.cursor()

            # Insertar o actualizar el código
            cursor.execute('INSERT OR REPLACE INTO codes (code, threshold) VALUES (?, ?)', (code, threshold))

            # Insertar o actualizar el UMB
            cursor.execute('INSERT OR IGNORE INTO UMB (umb) VALUES (?)', (umb,))

            # Asociar el código con el UMB
            cursor.execute('INSERT OR REPLACE INTO umb_codes (umb, code) VALUES (?, ?)', (umb, code))

            conn.commit()
            conn.close()

            # Actualizar los datos en la interfaz
            codes, UMB
            codes[code] = threshold
            if umb in UMB:
                UMB[umb].append(code)
            else:
                UMB[umb] = [code]

            # Actualizar el menú desplegable con los nuevos códigos
            self.code_dropdown['values'] = list(codes.keys())
            self.code_var.set(str(code))

            self.text_area.insert(tk.END, f"Código {code} agregado con umbral {threshold} y UMB {umb}\n")
            self.add_window.destroy()
        else:
            messagebox.showerror("Error", "Código inválido")

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()