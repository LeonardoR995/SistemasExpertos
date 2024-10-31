import tkinter as tk
from tkinter import scrolledtext
from itertools import product

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

def procesar_proposiciones():
    global operadores_list, proposiciones_simples_list, formulas, proposiciones_map
    operadores_list = []
    proposiciones_simples_list = []
    formulas = []
    proposiciones_map = {}
    proposiciones = entrada_proposiciones.get("1.0", tk.END).strip().lower().split("\n")

    letra_current = 0

    for proposicion in proposiciones:
        if proposicion:
            operadores, proposiciones_simples = identificar_operadores(proposicion)
            for simple in proposiciones_simples:
                key = simple.lstrip('¬').strip()
                if key not in proposiciones_map:
                    proposiciones_map[key] = chr(65 + letra_current)
                    letra_current += 1

            formula = ''
            for i in range(len(proposiciones_simples)):
                if i > 0:
                    if operadores[i - 1] == 'and':
                        formula += ' ∧ '
                    else:
                        formula += ' ∨ '
                prop_key = proposiciones_simples[i].lstrip('¬').strip()
                if not proposiciones_simples[i].startswith('¬'):
                    formula += proposiciones_map[prop_key]
                else:
                    formula += '¬' + proposiciones_map[prop_key]

            operadores_list.append(operadores)
            proposiciones_simples_list.append(proposiciones_simples)
            formulas.append(formula)

    if operadores_list and proposiciones_simples_list:
        text_result = ""
        for idx, (ops, props, form) in enumerate(zip(operadores_list, proposiciones_simples_list, formulas)):
            text_result += f"Proposición {idx + 1}:\n"
            text_result += f"Operadores identificados: {', '.join(ops).upper()}\n"
            text_result += f"Proposiciones simples:\n"
            for i, prop in enumerate(props):
                prop_key = prop.lstrip('¬').strip()
                text_result += f"{proposiciones_map[prop_key]}: {prop.replace('¬', '').strip()}\n"
            text_result += f"Fórmula: {form}\n\n"
        etiqueta_resultado.config(text=text_result)
        boton_cerrar.pack()
    else:
        etiqueta_resultado.config(text="Proposición no válida")

def cerrar_y_mostrar():
    ventana.destroy()
    for operadores, proposiciones_simples, formula in zip(operadores_list, proposiciones_simples_list, formulas):
        mostrar_tabla_verdad(operadores, proposiciones_simples)
        mostrar_arbol(operadores, proposiciones_simples, formula)

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
    ventana_tabla.title(f"Tabla de verdad")
    texto = scrolledtext.ScrolledText(ventana_tabla, width=70, height=15)
    texto.pack()

    headers = ' | '.join([proposiciones_map[prop.lstrip('¬').strip()] for prop in proposiciones_simples]) + " | Resultado\n"
    texto.insert(tk.END, headers)
    texto.insert(tk.END, "--|" * (len(proposiciones_simples) + 1) + "----------\n")

    for valores in product([1, 0], repeat=len(proposiciones_simples)):
        valores_negados = [
            int(not val) if proposiciones_simples[i].startswith('¬') else val
            for i, val in enumerate(valores)
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
        canvas.create_text(x0 + x_offset, y0 - 40 + y_offset, text=f"{proposiciones_map[prop.lstrip('¬').strip()]}: {prop.replace('¬', '').strip()}", font=("Arial", 12, "bold"))

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

ventana = tk.Tk()
ventana.title("Analizador de Proposiciones")
ventana.configure(bg="#eaeaea")

# Título
titulo = tk.Label(ventana, text="Analizador de Proposiciones", font=("Arial", 16, "bold"), bg="#eaeaea")
titulo.pack(pady=10)

# Entrada de proposiciones
tk.Label(ventana, text="Ingresa las proposiciones (una por línea):", bg="#eaeaea").pack()
entrada_proposiciones = tk.Text(ventana, height=10, width=50)
entrada_proposiciones.pack(pady=5)

# Botón para procesar
boton_procesar = tk.Button(ventana, text="Procesar", command=procesar_proposiciones)
boton_procesar.pack(pady=5)

# Etiqueta para mostrar resultados
etiqueta_resultado = tk.Label(ventana, text="", bg="#eaeaea", justify=tk.LEFT)
etiqueta_resultado.pack(pady=5)

# Botón para cerrar
boton_cerrar = tk.Button(ventana, text="Cerrar", command=cerrar_y_mostrar)
boton_cerrar.pack(pady=5)

ventana.mainloop()
