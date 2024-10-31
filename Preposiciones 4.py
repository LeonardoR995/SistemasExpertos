import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from itertools import product

# Variables globales
proposiciones_simples = set()  # Usar un conjunto para evitar duplicados
formulas = []  # Lista para almacenar fórmulas generadas

def identificar_operadores(proposicion):
    proposicion = proposicion.lower()
    operadores = []
    tokens = proposicion.split()
    temp_proposicion = []
    negacion = False

    for token in tokens:
        if token == "no":
            negacion = True
        elif token in ["y", "and", "o", "or"]:
            operadores.append("and" if token in ["y", "and"] else "or")
            proposicion_texto = " ".join(temp_proposicion).strip()
            if negacion:
                proposiciones_simples.add("¬" + proposicion_texto)
                negacion = False
            else:
                proposiciones_simples.add(proposicion_texto)
            temp_proposicion = []
        else:
            temp_proposicion.append(token)

    proposicion_texto = " ".join(temp_proposicion).strip()
    if negacion:
        proposiciones_simples.add("¬" + proposicion_texto)
    else:
        proposiciones_simples.add(proposicion_texto)

    return operadores, list(proposiciones_simples)

def procesar_proposicion():
    global operadores, formula
    proposicion = entrada_proposicion.get().lower()
    operadores, proposiciones_simples = identificar_operadores(proposicion)

    if operadores and proposiciones_simples:
        formula = 'A' if not proposiciones_simples[0].startswith('¬') else '¬A'
        for i in range(1, len(proposiciones_simples)):
            if operadores[i - 1] == 'and':
                formula += ' ∧ '
            else:
                formula += ' ∨ '
            formula += chr(65 + i) if not proposiciones_simples[i].startswith('¬') else '¬' + chr(65 + i)

        text_result = f"Operadores identificados: {', '.join(operadores).upper()}\nProposiciones simples:\n"
        for i, prop in enumerate(proposiciones_simples):
            text_result += f"{chr(65 + i)}: {prop.replace('¬', '').strip()}\n"
        text_result += f"Fórmula: {formula}"
        etiqueta_resultado.config(text=text_result)

        # Guardar la fórmula en la lista
        formulas.append((proposicion, formula))
        boton_cerrar.pack()
    else:
        etiqueta_resultado.config(text="Proposición no válida")

def guardar_regla():
    if not formulas:
        messagebox.showwarning("Advertencia", "No hay reglas para guardar.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:  # Especificar la codificación
            for proposicion, formula in formulas:
                f.write(f"{proposicion} => {formula}\n")
        messagebox.showinfo("Éxito", "Reglas guardadas exitosamente.")


def cargar_reglas():
    filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filepath:
        with open(filepath, 'r') as f:
            reglas = f.readlines()
        ventana_carga = tk.Tk()
        ventana_carga.title("Reglas Cargadas")
        texto = scrolledtext.ScrolledText(ventana_carga, width=70, height=15)
        texto.pack(padx=10, pady=10)
        for regla in reglas:
            texto.insert(tk.END, regla.strip() + "\n")
        ventana_carga.mainloop()

def cerrar_y_mostrar():
    ventana.destroy()
    # Mostrar tabla y árbol, asegurando que los datos sean correctos
    mostrar_tabla_verdad(operadores, list(proposiciones_simples))
    mostrar_arbol(operadores, list(proposiciones_simples), formula)

def evaluar_resultado(valores, operadores):
    resultado = valores[0]
    for i in range(1, len(valores)):
        if operadores[i - 1] == 'and':
            resultado = resultado and valores[i]
        else:
            resultado = resultado or valores[i]
    return int(resultado)

def mostrar_tabla_verdad(operadores, proposiciones_simples):
    ventana_tabla = tk.Tk()
    ventana_tabla.title("Tabla de verdad")
    texto = scrolledtext.ScrolledText(ventana_tabla, width=70, height=15)
    texto.pack(padx=10, pady=10)

    texto.insert(tk.END, "Tabla de verdad:\n\n")
    headers = ' | '.join([chr(65 + i) for i in range(len(proposiciones_simples))]) + " | Resultado\n"
    texto.insert(tk.END, headers)
    texto.insert(tk.END, "--|" * (len(proposiciones_simples) + 1) + "----------\n")

    for valores in product([1, 0], repeat=len(proposiciones_simples)):
        valores_negados = [
            int(not val) if prop.startswith('¬') else val
            for prop, val in zip(proposiciones_simples, valores)
        ]
        resultado = evaluar_resultado(valores_negados, operadores)
        valores_str = ' | '.join(map(str, valores_negados)) + f" | {resultado}\n"
        texto.insert(tk.END, valores_str)

    ventana_tabla.mainloop()

def mostrar_arbol(operadores, proposiciones_simples, formula):
    ventana_arbol = tk.Tk()
    ventana_arbol.title("Diagrama de árbol")
    frame = tk.Frame(ventana_arbol)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame, bg="white")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    scrollbar_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.xview)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

    x0, y0 = 1500, 700
    dx, dy = 38, 45
    canvas.create_text(x0, y0 - 80, text=f"Fórmula: {formula}", font=("Arial", 14, "bold"), fill="darkred")

    for i, prop in enumerate(proposiciones_simples):
        x_offset = ((i % 3) - 1) * 200
        y_offset = (i // 3) * 20
        canvas.create_text(x0 + x_offset, y0 - 40 + y_offset, text=f"{chr(65 + i)}: {prop.replace('¬', '').strip()}", font=("Arial", 12, "bold"))

    def asignar_valores_y_evaluar(caminos):
        valores = [int(val[-1]) for val in caminos]
        return evaluar_resultado(valores, operadores)

    def dibujar_nodos(prev_x, prev_y, depth, camino_actual):
        if depth == len(proposiciones_simples):
            resultado = asignar_valores_y_evaluar(camino_actual)
            canvas.create_text(prev_x, prev_y + 20, text=f"R={resultado}", font=("Arial", 10, "bold"), fill="blue")
            return

        x_izq = prev_x - (dx / 2) * (2 ** (len(proposiciones_simples) - depth - 1))
        y_izq = prev_y + dy
        nodo_izq = f"{chr(65 + depth)}=0"
        canvas.create_text(x_izq, y_izq, text=nodo_izq, font=("Arial", 10, "bold"), fill="red")
        canvas.create_line(prev_x, prev_y, x_izq, y_izq)
        dibujar_nodos(x_izq, y_izq, depth + 1, camino_actual + [nodo_izq])

        x_der = prev_x + (dx / 2) * (2 ** (len(proposiciones_simples) - depth - 1))
        y_der = prev_y + dy
        nodo_der = f"{chr(65 + depth)}=1"
        canvas.create_text(x_der, y_der, text=nodo_der, font=("Arial", 10, "bold"), fill="red")
        canvas.create_line(prev_x, prev_y, x_der, y_der)
        dibujar_nodos(x_der, y_der, depth + 1, camino_actual + [nodo_der])

    dibujar_nodos(x0, y0, 0, [])
    ventana_arbol.mainloop()

# Configuración de la interfaz
ventana = tk.Tk()
ventana.title("Analizador de Proposiciones")
ventana.geometry("500x350")
ventana.config(bg="#f0f0f0")

tk.Label(ventana, text="Ingresa la proposición:", bg="#f0f0f0").pack(pady=10)
entrada_proposicion = tk.Entry(ventana, width=70)
entrada_proposicion.pack(pady=5)
boton_procesar = tk.Button(ventana, text="Procesar", command=procesar_proposicion, bg="#4CAF50", fg="white")
boton_procesar.pack(pady=10)
boton_guardar = tk.Button(ventana, text="Guardar Regla", command=guardar_regla, bg="#2196F3", fg="white")
boton_guardar.pack(pady=5)
boton_cargar = tk.Button(ventana, text="Cargar Reglas", command=cargar_reglas, bg="#FF9800", fg="white")
boton_cargar.pack(pady=5)
etiqueta_resultado = tk.Label(ventana, text="", bg="#f0f0f0")
etiqueta_resultado.pack(pady=10)
boton_cerrar = tk.Button(ventana, text="Cerrar y mostrar resultados", command=cerrar_y_mostrar, bg="#f44336", fg="white")
boton_cerrar.pack_forget()

ventana.mainloop()
