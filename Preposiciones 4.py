import tkinter as tk
from tkinter import simpledialog, scrolledtext, filedialog, messagebox
from itertools import product

# Lista para almacenar las fórmulas
formulas = []
proposiciones_map = {}

# Función para guardar fórmulas en un archivo de texto
def guardar_formulas():
    if not formulas:
        messagebox.showwarning("Advertencia", "No hay fórmulas para guardar.")
        return
    archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
    if archivo:
        try:
            with open(archivo, "w", encoding='utf-8') as file:  # Usa codificación UTF-8
                for i, formula in enumerate(formulas):
                    # Reemplazar caracteres problemáticos con su equivalente textual
                    formula = formula.replace('∧', 'And')  # Conjunción
                    formula = formula.replace('∨', 'Or')   # Disyunción
                    
                    # Cambiar ¬ por Not en lugar de NOT
                    formula = formula.replace('¬', '-')  # Negación

                    file.write(f"Proposición {i + 1}: {formula}\n")
            messagebox.showinfo("Guardado", "Las fórmulas se guardaron correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")



# Función para cargar fórmulas desde un archivo de texto y mostrarlas en una nueva ventana
def cargar_formulas():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
    if archivo:
        try:
            with open(archivo, "r", encoding='utf-8') as file:
                contenido = file.read()
            mostrar_contenido_archivo(contenido)  # Mostrar en nueva ventana
            messagebox.showinfo("Cargado", "Las fórmulas se cargaron correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

# Función para cargar reglas desde un archivo y mostrarlas en la entrada de proposiciones
def cargar_reglas():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
    if archivo:
        try:
            with open(archivo, "r", encoding='utf-8') as file:
                contenido = file.read()
                # Cargar el contenido del archivo en el área de texto de las proposiciones
                entrada_proposiciones.delete("1.0", tk.END)  # Limpiar el área de texto antes de cargar
                entrada_proposiciones.insert(tk.END, contenido)  # Insertar el contenido en la entrada
            messagebox.showinfo("Cargado", "Las reglas se cargaron correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")


# Función para mostrar el contenido del archivo en una nueva ventana
def mostrar_contenido_archivo(contenido):
    ventana_contenido = tk.Toplevel()  # Crear nueva ventana
    ventana_contenido.title("Contenido del Archivo")
    ventana_contenido.configure(bg="#f7f7f7")

    # Crear un área de texto para mostrar el contenido
    texto_contenido = scrolledtext.ScrolledText(ventana_contenido, width=70, height=20, font=("Helvetica", 10))
    texto_contenido.pack(padx=10, pady=10)
    texto_contenido.insert(tk.END, contenido)
    texto_contenido.config(state=tk.DISABLED)  # Hacer que el área de texto sea solo lectura

    # Botón para cerrar la ventana
    boton_cerrar = tk.Button(ventana_contenido, text="Cerrar", command=ventana_contenido.destroy)
    boton_cerrar.pack(pady=5)


# Función para identificar operadores y proposiciones
def identificar_operadores(proposicion):
    proposicion = proposicion.lower()
    operadores = []
    proposiciones_simples = []
    tokens = proposicion.split()
    temp_proposicion = []
    negacion = False

    for token in tokens:
        if token == "no":
            negacion = True
        elif token in ["y", "and", "o", "or"]:
            if temp_proposicion:
                proposicion_texto = " ".join(temp_proposicion).strip()
                if negacion:
                    proposiciones_simples.append("¬" + proposicion_texto)
                    negacion = False
                else:
                    proposiciones_simples.append(proposicion_texto)
                temp_proposicion = []
            operadores.append("and" if token in ["y", "and"] else "or")
        else:
            temp_proposicion.append(token)

    if temp_proposicion:
        proposicion_texto = " ".join(temp_proposicion).strip()
        if negacion:
            proposiciones_simples.append("¬" + proposicion_texto)
        else:
            proposiciones_simples.append(proposicion_texto)

    return operadores, proposiciones_simples

# Función para procesar las proposiciones
def procesar_proposiciones():
    global operadores_list, proposiciones_simples_list, formulas, proposiciones_map
    operadores_list = []
    proposiciones_simples_list = []
    formulas = []
    proposiciones_map = {}
    letra_current = 1
    proposiciones = entrada_proposiciones.get("1.0", tk.END).strip().lower().split("\n")

    for proposicion in proposiciones:
        if proposicion:
            operadores, proposiciones_simples = identificar_operadores(proposicion)
            proposiciones_simplificadas = []

            for simple in proposiciones_simples:
                key = simple.lstrip('¬').strip()
                if key not in proposiciones_map:
                    proposiciones_map[key] = f"A{letra_current}"
                    letra_current += 1
                proposiciones_simplificadas.append(simple)

            formula = ''
            for i in range(len(proposiciones_simplificadas)):
                if i > 0:
                    if operadores[i - 1] == 'and':
                        formula += ' ∧ '
                    else:
                        formula += ' ∨ '
                prop_key = proposiciones_simplificadas[i].lstrip('¬').strip()
                if not proposiciones_simplificadas[i].startswith('¬'):
                    formula += proposiciones_map[prop_key]
                else:
                    formula += '¬' + proposiciones_map[prop_key]

            operadores_list.append(operadores)
            proposiciones_simples_list.append(proposiciones_simplificadas)
            formulas.append(formula)

    if operadores_list and proposiciones_simples_list:
        mostrar_detalles_proposicion()

# Función para mostrar detalles de la proposición
def mostrar_detalles_proposicion():
    seleccion = simpledialog.askstring("Seleccionar proposición", "Elige la proposición (ej. 1, 2, 3):", initialvalue="1")

    try:
        seleccion = int(seleccion) - 1
        if 0 <= seleccion < len(operadores_list):
            ventana_detalles = tk.Toplevel()
            ventana_detalles.title("Detalles de la Proposición")
            ventana_detalles.configure(bg="#f7f7f7")

            encabezado = f"Detalles de la Proposición #{seleccion + 1}"
            etiqueta_encabezado = tk.Label(ventana_detalles, text=encabezado, font=("Helvetica", 14, "bold"), bg="#f7f7f7")
            etiqueta_encabezado.pack(pady=10)

            texto_detalles = scrolledtext.ScrolledText(ventana_detalles, width=70, height=15, font=("Helvetica", 10))
            texto_detalles.pack(padx=10, pady=10)
            texto_detalles.configure(bg="#ffffff", highlightbackground="#dddddd")

            detalles = ""
            for simple in proposiciones_simples_list[seleccion]:
                prop_key = simple.lstrip('¬').strip()
                detalles += f"{proposiciones_map[prop_key]}: {prop_key}\n"
            detalles += f"\nFórmula: {formulas[seleccion]}\n"
            texto_detalles.insert(tk.END, detalles)
            texto_detalles.config(state=tk.DISABLED)

            variables_frame = tk.Frame(ventana_detalles, bg="#f7f7f7")
            variables_frame.pack(pady=5)

            # Agregar una etiqueta para el texto que dice "Seleccione los átomos verdaderos"
            etiqueta_seleccion = tk.Label(variables_frame, text="Seleccione los átomos verdaderos", font=("Helvetica", 12), bg="#f7f7f7")
            etiqueta_seleccion.pack(pady=10)

            checkboxes = []
            for simple in proposiciones_simples_list[seleccion]:
                var_key = simple.lstrip('¬').strip()
                var_value = tk.IntVar()
                checkbox = tk.Checkbutton(variables_frame, text=f"{proposiciones_map[var_key]}: {var_key}", variable=var_value, bg="#f7f7f7", font=("Helvetica", 10))
                checkbox.pack(anchor='w', padx=10)
                checkboxes.append((var_key, var_value))

            boton_cerrar = tk.Button(ventana_detalles, text="Cerrar y Mostrar Tabla de Verdad", font=("Helvetica", 10), bg="#007acc", fg="white",
                                     command=lambda: [ventana_detalles.destroy(), mostrar_tabla_verdad(operadores_list[seleccion], proposiciones_simples_list[seleccion], formulas[seleccion], checkboxes)])
            boton_cerrar.pack(pady=10)

        else:
            etiqueta_resultado.config(text="Selección no válida", fg="red")
    except ValueError:
        etiqueta_resultado.config(text="Por favor, introduce un número válido", fg="red")


def evaluar_resultado(valores, operadores):
    resultado = valores[0]
    for i in range(1, len(valores)):
        if i - 1 < len(operadores):  
            if operadores[i - 1] == 'and':
                resultado = resultado and valores[i]
            else:
                resultado = resultado or valores[i]
    return int(resultado)

def mostrar_tabla_verdad(operadores, proposiciones_simples, formula, checkboxes):
    ventana_tabla = tk.Toplevel()
    ventana_tabla.title("Tabla de verdad")
    texto = scrolledtext.ScrolledText(ventana_tabla, width=70, height=15)
    texto.pack()

    headers = ' | '.join([proposiciones_map[prop.lstrip('¬').strip()] for prop in proposiciones_simples]) + " | Resultado\n"
    texto.insert(tk.END, headers)
    texto.insert(tk.END, "--|" * (len(proposiciones_simples) + 1) + "----------\n")

    valores_seleccionados = [var.get() for _, var in checkboxes]
    resultado_seleccionado = None

    for valores in product([0, 1], repeat=len(proposiciones_simples)):
        valores_negados = [
            int(not val) if proposiciones_simples[i].startswith('¬') else val
            for i, val in enumerate(valores)
        ]
        resultado = evaluar_resultado(valores_negados, operadores)
        valores_str = ' | '.join(map(str, valores)) + f" | {resultado}\n"
        texto.insert(tk.END, valores_str)

        if list(valores) == valores_seleccionados:
            resultado_seleccionado = resultado

    # Resaltar la fila correspondiente a los valores seleccionados
    if resultado_seleccionado is not None:
        texto.insert(tk.END, f"Valores seleccionados: {' | '.join(map(str, valores_seleccionados))} | {resultado_seleccionado}\n", 'highlight')

    # Configurar el tag de resaltado para el texto
    texto.tag_config('highlight', foreground='blue')

    boton_cerrar = tk.Button(ventana_tabla, text="Cerrar y Mostrar Árbol", command=lambda: [ventana_tabla.destroy(), mostrar_arbol(operadores, proposiciones_simples, formula)])
    boton_cerrar.pack()

    return ventana_tabla

def mostrar_arbol(operadores, proposiciones_simples, formula):
    ventana_arbol = tk.Tk()
    ventana_arbol.title("Diagrama de árbol")

    frame = tk.Frame(ventana_arbol)
    frame.pack(fill=tk.BOTH, expand=True)
    
    canvas = tk.Canvas(frame, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True)
    
    scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    scrollbar_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.xview)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    
    x0, y0 = 1500, 700  # Coordenada inicial centrada (ajustada hacia abajo)
    dx, dy = 38, 45  # Separación entre nodos

    # Mostrar la fórmula en la parte superior del canvas
    canvas.create_text(x0, y0 - 80, text=f"Fórmula: {formula}", font=("Arial", 14, "bold"), fill="darkred")

    # Mostrar la variable y su contenido en la parte superior
    variables_contenido = ', '.join([f"{chr(65 + i)}={valor}" for i, valor in enumerate(proposiciones_simples)])
    canvas.create_text(x0, y0 - 50, text=f"Variables: {variables_contenido}", font=("Arial", 12, "bold"), fill="blue")

    def asignar_valores_y_evaluar(caminos):
        # Convierte el camino en valores de verdad y evalúa
        valores = [int(val[-1]) for val in caminos]
        return evaluar_resultado(valores, operadores)

    def dibujar_nodos(prev_x, prev_y, depth, camino_actual):
        if depth == len(proposiciones_simples):  # Si es nodo hoja, muestra el resultado
            resultado = asignar_valores_y_evaluar(camino_actual)  # Evalúa el resultado de la rama
            # Mostrar el resultado (0 o 1) en la hoja
            hoja_texto = f"R={resultado}"
            canvas.create_text(prev_x, prev_y + 20, text=hoja_texto, font=("Arial", 10, "bold"), fill="blue")
            return
        
        # Nodo izquierdo para valor 0
        x_izq = prev_x - (dx / 2) * (2 ** (len(proposiciones_simples) - depth - 1))
        y_izq = prev_y + dy
        nodo_izq = f"{chr(65 + depth)}=0"
        canvas.create_text(x_izq, y_izq, text=nodo_izq, font=("Arial", 10))
        canvas.create_line(prev_x, prev_y, x_izq, y_izq)
        dibujar_nodos(x_izq, y_izq, depth + 1, camino_actual + [nodo_izq])
        
        # Nodo derecho para valor 1
        x_der = prev_x + (dx / 2) * (2 ** (len(proposiciones_simples) - depth - 1))
        y_der = prev_y + dy
        nodo_der = f"{chr(65 + depth)}=1"
        canvas.create_text(x_der, y_der, text=nodo_der, font=("Arial", 10))
        canvas.create_line(prev_x, prev_y, x_der, y_der)
        dibujar_nodos(x_der, y_der, depth + 1, camino_actual + [nodo_der])


    # Iniciar el dibujo del árbol desde la raíz
    dibujar_nodos(x0, y0, 0, [])

    ventana_arbol.mainloop()


# Configuración de la ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Procesador de Proposiciones Lógicas")
ventana_principal.configure(bg="#f7f7f7")

# Título principal
titulo_principal = tk.Label(ventana_principal, text="Procesador de Proposiciones Lógicas", font=("Helvetica", 16, "bold"), bg="#f7f7f7")
titulo_principal.pack(pady=10)

# Instrucciones
etiqueta_instrucciones = tk.Label(ventana_principal, text="Introduce proposiciones lógicas (una por línea):", font=("Helvetica", 10), bg="#f7f7f7")
etiqueta_instrucciones.pack(pady=5)

# Entrada de proposiciones
entrada_proposiciones = scrolledtext.ScrolledText(ventana_principal, width=70, height=10, font=("Helvetica", 10))
entrada_proposiciones.pack(pady=5)
entrada_proposiciones.configure(bg="#ffffff", highlightbackground="#dddddd")

# Botón para procesar
boton_procesar = tk.Button(ventana_principal, text="Procesar Proposiciones", font=("Helvetica", 10), bg="#007acc", fg="white", command=procesar_proposiciones)
boton_procesar.pack(pady=10)

# Botón para guardar fórmulas
boton_guardar_formulas = tk.Button(ventana_principal, text="Guardar Fórmulas", font=("Helvetica", 10), bg="#28a745", fg="white", command=guardar_formulas)
boton_guardar_formulas.pack(pady=5)

# Botón para cargar fórmulas
boton_cargar_formulas = tk.Button(ventana_principal, text="Cargar Fórmulas", font=("Helvetica", 10), bg="#17a2b8", fg="white", command=cargar_formulas)
boton_cargar_formulas.pack(pady=5)

# Etiqueta para mostrar mensajes
etiqueta_resultado = tk.Label(ventana_principal, text="", font=("Helvetica", 10), bg="#f7f7f7")
etiqueta_resultado.pack(pady=5)

# Botón para cargar reglas desde un archivo
boton_cargar_reglas = tk.Button(ventana_principal, text="Cargar Reglas", font=("Helvetica", 10), bg="#17a2b8", fg="white", command=cargar_reglas)
boton_cargar_reglas.pack(pady=5)

ventana_principal.mainloop()

