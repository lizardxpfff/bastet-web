import tkinter as tk
import tkinter.messagebox as messagebox
import requests
import sqlite3

# Función para obtener la dirección desde la API de Google Maps
def obtener_direccion(latitud, longitud):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitud},{longitud}&key=null"  
    response = requests.get(url)
    data = response.json()
    direccion = data['results'][0]['formatted_address']
    return direccion

# Función para almacenar la ubicación de una cámara en la base de datos
def almacenar_camara(entry_latitud_camara, entry_longitud_camara, entry_propietario_camara, entry_contacto_camara):
    latitud = entry_latitud_camara.get()
    longitud = entry_longitud_camara.get()
    propietario = entry_propietario_camara.get()
    contacto = entry_contacto_camara.get()
    
    if not latitud or not longitud or not propietario or not contacto:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return
    
    conn = sqlite3.connect('camaras.db')
    cursor = conn.cursor()
    
    # Guardar los datos de la cámara en la base de datos
    cursor.execute("INSERT INTO camaras (latitud, longitud, propietario, contacto) VALUES (?, ?, ?, ?)",
                   (latitud, longitud, propietario, contacto))
    
    conn.commit()
    conn.close()
    
    # Limpiar campos del formulario
    entry_latitud_camara.delete(0, tk.END)
    entry_longitud_camara.delete(0, tk.END)
    entry_propietario_camara.delete(0, tk.END)
    entry_contacto_camara.delete(0, tk.END)
    
    messagebox.showinfo("Éxito", "Los datos han sido guardados con éxito.")

# Función para buscar cámaras cercanas
def buscar_camaras():
    latitud = entry_latitud.get()
    longitud = entry_longitud.get()
    direccion = obtener_direccion(latitud, longitud)
    
    conn = sqlite3.connect('camaras.db')
    cursor = conn.cursor()
    
    # Radio de 200 metros en grados (~0.0018 grados)
    radio = 0.0018
    
    cursor.execute("SELECT * FROM camaras WHERE latitud BETWEEN ? AND ? AND longitud BETWEEN ? AND ?",
                   (float(latitud)-radio, float(latitud)+radio, float(longitud)-radio, float(longitud)+radio))
    camaras_cercanas = cursor.fetchall()
    
    mensaje = f"Dirección: {direccion}\n\nCámaras cercanas:\n"
    for camara in camaras_cercanas:
        mensaje += f"\nPropietario: {camara[3]}\nCoordenadas: {camara[1]}, {camara[2]}\nContacto: {camara[4]}\n\n"
    
    messagebox.showinfo("Resultado de la búsqueda", mensaje)
    
    conn.close()

# Función para limpiar los campos de entrada
def limpiar_campos():
    entry_latitud.delete(0, tk.END)
    entry_longitud.delete(0, tk.END)

# Función para abrir el submenú de agregar cámara
def abrir_submenu_agregar_camara():
    ventana_agregar_camara = tk.Toplevel(root)
    ventana_agregar_camara.title("Agregar Cámara")
    
    # Elementos para ingresar datos de la cámara
    label_latitud_camara = tk.Label(ventana_agregar_camara, text="Latitud:")
    label_latitud_camara.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    entry_latitud_camara = tk.Entry(ventana_agregar_camara)
    entry_latitud_camara.grid(row=0, column=1, padx=10, pady=10)

    label_longitud_camara = tk.Label(ventana_agregar_camara, text="Longitud:")
    label_longitud_camara.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    entry_longitud_camara = tk.Entry(ventana_agregar_camara)
    entry_longitud_camara.grid(row=1, column=1, padx=10, pady=10)

    label_propietario_camara = tk.Label(ventana_agregar_camara, text="Propietario:")
    label_propietario_camara.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    entry_propietario_camara = tk.Entry(ventana_agregar_camara)
    entry_propietario_camara.grid(row=2, column=1, padx=10, pady=10)

    label_contacto_camara = tk.Label(ventana_agregar_camara, text="Contacto:")
    label_contacto_camara.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    entry_contacto_camara = tk.Entry(ventana_agregar_camara)
    entry_contacto_camara.grid(row=3, column=1, padx=10, pady=10)

    boton_guardar_camara = tk.Button(ventana_agregar_camara, text="Guardar Datos", command=lambda: almacenar_camara(entry_latitud_camara, entry_longitud_camara, entry_propietario_camara, entry_contacto_camara))
    boton_guardar_camara.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Crear la ventana principal
root = tk.Tk()
root.title("Consulta de Cámaras")

# Tamaño de la ventana
root.geometry("500x400")

# Configurar el fondo y el color de los botones
root.configure(bg="#1E3A5F")  # Fondo de la ventana azul
btn_color = "#4A90E2"  # Color de los botones (azul claro)
btn_hover_color = "#1C3D6D"  # Color de hover para los botones

# Función para cambiar color al hacer hover sobre el botón
def on_enter(e):
    e.widget['background'] = btn_hover_color

def on_leave(e):
    e.widget['background'] = btn_color

# Botones para buscar cámaras, limpiar campos y salir
boton_buscar = tk.Button(root, text="Buscar Cámaras", command=buscar_camaras, bg=btn_color, fg="white", font=("Arial", 12))
boton_buscar.grid(row=0, column=1, padx=10, pady=10)

boton_limpiar = tk.Button(root, text="Limpiar", command=limpiar_campos, bg=btn_color, fg="white", font=("Arial", 12))
boton_limpiar.grid(row=1, column=0, padx=10, pady=10)

boton_salir = tk.Button(root, text="Salir", command=root.quit, bg=btn_color, fg="white", font=("Arial", 12))
boton_salir.grid(row=1, column=1, padx=10, pady=10)

# Botón para abrir el submenú de agregar cámara
boton_agregar_camara = tk.Button(root, text="Agregar Cámara", command=abrir_submenu_agregar_camara, bg=btn_color, fg="white", font=("Arial", 12))
boton_agregar_camara.grid(row=0, column=0, padx=10, pady=10)

# Elementos para ingresar datos de la cámara
label_latitud = tk.Label(root, text="Latitud:", bg="#1E3A5F", fg="white", font=("Arial", 12))
label_latitud.grid(row=2, column=0, padx=10, pady=10, sticky="w")

entry_latitud = tk.Entry(root, font=("Arial", 12))
entry_latitud.grid(row=2, column=1, padx=10, pady=10)

label_longitud = tk.Label(root, text="Longitud:", bg="#1E3A5F", fg="white", font=("Arial", 12))
label_longitud.grid(row=3, column=0, padx=10, pady=10, sticky="w")

entry_longitud = tk.Entry(root, font=("Arial", 12))
entry_longitud.grid(row=3, column=1, padx=10, pady=10)

root.mainloop()
