import json
import os
import sqlite3
import shutil
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext

# Configura rutas
json_file_path = 'data/usuarios.json'
pin_file_path = 'protected/secret_pin.txt'
db_file = 'mi_base_de_datos.db'
initial_data_path = 'data/initial_data.json'

# Asegúrate de que las carpetas y archivos necesarios existan
def ensure_directories_and_files():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('protected'):
        os.makedirs('protected')

    # Si el archivo JSON no existe, créalo con datos iniciales
    if not os.path.exists(json_file_path):
        if os.path.exists(initial_data_path):
            shutil.copy(initial_data_path, json_file_path)
        else:
            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump([], file, ensure_ascii=False, indent=4)

    # Si el archivo del PIN no existe, créalo (puedes poner un PIN predeterminado si lo deseas)
    if not os.path.exists(pin_file_path):
        with open(pin_file_path, 'w', encoding='utf-8') as file:
            file.write('1234')  # Puedes cambiar '1234' por el PIN que prefieras

# Funciones para manejar la base de datos
def get_db_connection():
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()  # Crear un cursor para ejecutar comandos SQL

    # Crear la tabla si no existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        edad INTEGER,
        email TEXT UNIQUE
    )
    ''')

    # Verificar si la tabla está vacía
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    count = cursor.fetchone()[0]

    if count == 0:
        # Insertar datos iniciales si la tabla está vacía
        initial_data = [
            {"nombre": "Juan Pérez", "edad": 30, "email": "juan.perez@example.com"},
            {"nombre": "Ana Gómez", "edad": 25, "email": "ana.gomez@example.com"},
        ]
        for user in initial_data:
            cursor.execute('''
            INSERT INTO usuarios (nombre, edad, email) VALUES (?, ?, ?)
            ''', (user['nombre'], user['edad'], user['email']))
    
    conn.commit()
    conn.close()

# Funciones para manejar el archivo JSON
def load_data_from_json():
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error al leer el archivo JSON: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []

def save_data_to_json(data):
    try:
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")

# Función para verificar el PIN
def verify_pin(pin):
    try:
        with open(pin_file_path, 'r', encoding='utf-8') as file:
            correct_pin = file.read().strip()
        return pin == correct_pin
    except Exception as e:
        print(f"Error al verificar el PIN: {e}")
        return False

# Crear la ventana principal
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Usuarios")

        # Configurar interfaz
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.text_area = scrolledtext.ScrolledText(self.frame, width=50, height=20)
        self.text_area.pack()

        self.load_button = tk.Button(self.frame, text="Cargar Usuarios", command=self.load_users)
        self.load_button.pack(pady=5)

        self.save_button = tk.Button(self.frame, text="Guardar Usuario", command=self.save_user)
        self.save_button.pack(pady=5)

        self.delete_button = tk.Button(self.frame, text="Eliminar Usuario", command=self.delete_user)
        self.delete_button.pack(pady=5)

        self.add_button = tk.Button(self.frame, text="Añadir Usuario", command=self.add_user)
        self.add_button.pack(pady=5)

    def load_users(self):
        usuarios = load_data_from_json()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, json.dumps(usuarios, indent=4))

    def save_user(self):
        try:
            usuarios = json.loads(self.text_area.get(1.0, tk.END))
            save_data_to_json(usuarios)
            messagebox.showinfo("Éxito", "Usuarios guardados correctamente.")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Error al procesar JSON: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el usuario: {e}")

    def delete_user(self):
        user_id = simpledialog.askinteger("Eliminar Usuario", "ID del usuario a eliminar:")
        if user_id is not None:
            usuarios = load_data_from_json()
            usuarios = [u for u in usuarios if u['id'] != user_id]
            save_data_to_json(usuarios)
            self.load_users()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")

    def add_user(self):
        user_name = simpledialog.askstring("Añadir Usuario", "Nombre del usuario:")
        user_age = simpledialog.askinteger("Añadir Usuario", "Edad del usuario:")
        user_email = simpledialog.askstring("Añadir Usuario", "Email del usuario:")
        if user_name and user_age and user_email:
            usuarios = load_data_from_json()
            new_user = {
                "id": (usuarios[-1]['id'] + 1 if usuarios else 1),
                "nombre": user_name,
                "edad": user_age,
                "email": user_email
            }
            usuarios.append(new_user)
            save_data_to_json(usuarios)
            self.load_users()
            messagebox.showinfo("Éxito", "Usuario añadido correctamente.")

if __name__ == '__main__':
    ensure_directories_and_files()  # Asegúrate de que las carpetas y archivos existan
    initialize_db()  # Asegúrate de que la base de datos esté inicializada
    root = tk.Tk()
    app = App(root)
    root.mainloop()
