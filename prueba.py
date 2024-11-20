import tkinter as tk

# Función para generar el árbol semántico según las nuevas reglas

def generar_arbol_semantico(formula):
    # Conjunción (𝛼 ∧ 𝛽) - Una sola rama vertical
    if '∧' in formula:
        operadores = formula.split('∧')     
        izquierda = operadores[0].strip(),operadores[1].strip()
        derecha = operadores[1].strip()
        # Para la conjunción, retornamos una única rama vertical
        return ('AND', izquierda, derecha)

    # Disyunción (𝛼 ∨ 𝛽) - Dos ramas
    elif '∨' in formula:
        operadores = formula.split('∨')
        izquierda = operadores[0].strip()
        derecha = operadores[1].strip()
        return ('OR', izquierda, derecha)

    # Negación de Conjunción (¬(𝛼 ∧ 𝛽)) -> ¬𝛼 ∨ ¬𝛽 - Dos ramas
    elif '¬(' in formula and '∧' in formula:
        formula_inner = formula[2:-1]  # Eliminar ¬( )
        operadores = formula_inner.split('∧')
        izquierda = '¬' + operadores[0].strip()
        derecha = '¬' + operadores[1].strip()
        return ('OR', izquierda, derecha)

    # Negación de Disyunción (¬(𝛼 ∨ 𝛽)) -> ¬𝛼 ∧ ¬𝛽 - Una sola rama vertical
    elif '¬(' in formula and '∨' in formula:
        formula_inner = formula[2:-1]  # Eliminar ¬( )
        operadores = formula_inner.split('∨')
        izquierda = '¬' + operadores[0].strip()
        derecha = '¬' + operadores[1].strip()
        return ('AND', izquierda, derecha)

    # Negación de Implicación (¬(𝛼 → 𝛽)) -> 𝛼 ∧ ¬𝛽 - Una sola rama vertical
    elif '¬(' in formula and '→' in formula:
        formula_inner = formula[2:-1]  # Eliminar ¬( )
        operadores = formula_inner.split('→')
        izquierda = operadores[0].strip()
        derecha = '¬' + operadores[1].strip()
        return ('AND', izquierda, derecha)

    # Negación de Bicondicional (¬(𝛼 ↔ 𝛽)) -> (𝛼 ∧ ¬𝛽) ∨ (𝛽 ∧ ¬𝛼) - Dos ramas
    elif '¬(' in formula and '↔' in formula:
        formula_inner = formula[2:-1]  # Eliminar ¬( )
        operadores = formula_inner.split('↔')
        izquierda = operadores[0].strip()
        derecha = operadores[1].strip()
        return ('OR', ('AND', izquierda, '¬' + derecha), ('AND', derecha, '¬' + izquierda))

    # Doble Negación (¬¬𝛼) -> ¬¬𝛼 = 𝛼 - Una sola proposición
    elif '¬¬' in formula:
        return formula[2:].strip()  # Eliminar las dos negaciones

    # Bicondicional (𝛼 ↔ 𝛽) -> (𝛼 ∧ 𝛽) ∨ (¬𝛼 ∧ ¬𝛽) - Dos ramas
    elif '↔' in formula:
        operadores = formula.split('↔')
        izquierda = operadores[0].strip()
        derecha = operadores[1].strip()
        return ('OR', ('AND', izquierda, derecha), ('AND', '¬' + izquierda, '¬' + derecha))

    # Implicación (𝛼 → 𝛽) -> ¬𝛼 ∨ 𝛽 - Dos ramas
    elif '→' in formula:
        operadores = formula.split('→')
        izquierda = '¬' + operadores[0].strip()
        derecha = operadores[1].strip()
        return ('OR', izquierda, derecha)

    # Si es una proposición simple, la devolvemos tal cual
    else:
        return formula.strip()

# Función para dibujar el árbol semántico según las reglas
def dibujar_arbol_semantico(arbol, canvas, x, y, dx, dy):
    if isinstance(arbol, tuple):
        operador, izquierda, derecha = arbol
        
        # Dibuja el operador
        canvas.create_text(x, y, text=operador, font=("Arial", 12, "bold"))
        
        # Si es AND o OR (con dos ramas), generamos dos ramas
        if operador == 'AND' or operador == 'OR':  
            x_izq = x - dx
            y_izq = y + dy
            x_der = x + dx
            y_der = y + dy
            canvas.create_line(x, y, x_izq, y_izq)
            canvas.create_line(x, y, x_der, y_der)
            dibujar_arbol_semantico(izquierda, canvas, x_izq, y_izq, dx / 2, dy)
            dibujar_arbol_semantico(derecha, canvas, x_der, y_der, dx / 2, dy)
        
        # Para operadores con una sola rama (como las negaciones), solo dibujamos una línea
        else:
            x_rama = x
            y_rama = y + dy
            canvas.create_line(x, y, x_rama, y_rama)
            dibujar_arbol_semantico(izquierda, canvas, x_rama, y_rama, dx / 2, dy)

    else:
        # Si es una proposición simple, dibujarla
        canvas.create_text(x, y, text=arbol, font=("Arial", 12))

# Función para mostrar el árbol semántico en la ventana
def mostrar_arbol_semantico(formula):
    ventana_arbol = tk.Toplevel()
    ventana_arbol.title("Árbol Semántico")
    
    canvas = tk.Canvas(ventana_arbol, bg="white", width=600, height=400)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    arbol = generar_arbol_semantico(formula)
    dibujar_arbol_semantico(arbol, canvas, 300, 50, 120, 60)

# Ventana principal
ventana = tk.Tk()
ventana.title("Generador de Árbol Semántico")
entrada_formula = tk.Entry(ventana, width=50)
entrada_formula.pack(padx=10, pady=10)
boton_mostrar_arbol = tk.Button(ventana, text="Generar Árbol Semántico", command=lambda: mostrar_arbol_semantico(entrada_formula.get()))
boton_mostrar_arbol.pack(padx=10, pady=10)
ventana.mainloop()