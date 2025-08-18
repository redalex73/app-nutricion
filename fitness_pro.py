# --- fitness_app_pro.py (Versión 2.4 - Final con Borrado de Historial) ---
import customtkinter as ctk
import requests
from tkinter import ttk, messagebox
import sqlite3
from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# --- 1. CONFIGURACIÓN Y CONSTANTES GLOBALES ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

APP_ID = "TU_ID_DE_NUTRITION_ANALYSIS"
APP_KEY = "TU_KEY_DE_NUTRITION_ANALYSIS"
DETAILS_API_URL = f"https://api.edamam.com/api/nutrition-details" 
DB_FILE = "fitness_data.db"

RECIPE_TRANSLATOR = {
    "arroz tres delicias": "1 cup white rice, 50g peas, 50g ham, 50g shrimp, 1 egg",
    "tortilla de patata": "2 medium potatoes, 3 eggs, 1 small onion, olive oil",
    "tortilla": "2 medium potatoes, 3 eggs, 1 small onion, olive oil",
    "lentejas": "1 cup lentils, 50g chorizo, 1 potato, 1 carrot"
}

# --- 2. FUNCIONES DE GESTIÓN DE BASE DE DATOS ---

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, tipo TEXT NOT NULL,
            descripcion TEXT NOT NULL, calorias INTEGER NOT NULL, proteinas REAL,
            ejercicio_tipo TEXT, duracion_min INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings ( key TEXT PRIMARY KEY, value REAL NOT NULL )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_recipes (
            dish_name TEXT PRIMARY KEY, ingredients TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('objetivo_calorias', 2200)")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('objetivo_proteinas', 150)")
    conn.commit()
    conn.close()

# NUEVO: Función específica para borrar solo los registros de seguimiento
def delete_all_log_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros")
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_setting(key, value):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
    conn.commit()
    conn.close()

def get_all_custom_recipes():
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("SELECT dish_name, ingredients FROM custom_recipes ORDER BY dish_name ASC")
    recipes = cursor.fetchall()
    conn.close()
    return recipes

def get_custom_recipe(dish_name):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("SELECT ingredients FROM custom_recipes WHERE dish_name = ?", (dish_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_custom_recipe(dish_name, ingredients):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO custom_recipes (dish_name, ingredients) VALUES (?, ?)", (dish_name.lower(), ingredients))
    conn.commit()
    conn.close()

def delete_custom_recipe(dish_name):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_recipes WHERE dish_name = ?", (dish_name.lower(),))
    conn.commit()
    conn.close()

def guardar_registro_en_db(registro):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO registros (fecha, tipo, descripcion, calorias, proteinas, ejercicio_tipo, duracion_min)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date.today().isoformat(), registro['tipo'], registro['descripcion'], registro['calorias'],
        registro.get('proteinas'), registro.get('ejercicio_tipo'), registro.get('duracion_min')
    ))
    conn.commit(); conn.close()

def cargar_datos_del_dia():
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("SELECT * FROM registros WHERE fecha = ?", (date.today().isoformat(),))
    registros = []
    for r in cursor.fetchall():
        registros.append({"tipo": r[2], "descripcion": r[3], "calorias": r[4], "proteinas": r[5] if r[5] is not None else "---", "ejercicio_tipo": r[6], "duracion_min": r[7]})
    conn.close(); return registros

def obtener_datos_historicos(dias=30):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    fecha_limite = date.today() - timedelta(days=dias - 1)
    query = "SELECT fecha, SUM(calorias), SUM(CASE WHEN tipo = 'Comida' THEN proteinas ELSE 0 END) FROM registros WHERE fecha >= ? GROUP BY fecha ORDER BY fecha ASC"
    cursor.execute(query, (fecha_limite.isoformat(),)); datos = cursor.fetchall(); conn.close()
    objetivo_calorias = get_setting('objetivo_calorias')
    fechas_completas = { (date.today() - timedelta(days=i)).isoformat(): {'calorias_netas': 0, 'proteinas': 0} for i in range(dias) }
    for row in datos:
        fechas_completas[row[0]] = {'calorias_netas': row[1], 'proteinas': row[2]}
    sorted_fechas = sorted(fechas_completas.keys())
    return {
        "fechas_labels": [f[-5:] for f in sorted_fechas],
        "calorias_netas": [fechas_completas[f]['calorias_netas'] for f in sorted_fechas],
        "proteinas": [fechas_completas[f]['proteinas'] for f in sorted_fechas],
        "objetivo_calorias": objetivo_calorias
    }

def obtener_promedio_nutrientes(dias=3):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    fecha_limite = date.today() - timedelta(days=dias)
    query = """
        SELECT
            SUM(CASE WHEN tipo = 'Comida' THEN calorias ELSE 0 END),
            SUM(CASE WHEN tipo = 'Comida' THEN proteinas ELSE 0 END),
            COUNT(DISTINCT fecha)
        FROM registros
        WHERE fecha > ? AND fecha < ?
    """
    cursor.execute(query, (fecha_limite.isoformat(), date.today().isoformat()))
    datos = cursor.fetchone(); conn.close()
    if not datos or not datos[2]:
        return {"promedio_cal": 0, "promedio_prot": 0, "dias_registrados": 0}
    total_cal, total_prot, num_dias = datos
    return {"promedio_cal": total_cal / num_dias if total_cal else 0, "promedio_prot": total_prot / num_dias if total_prot else 0, "dias_registrados": num_dias}

def generar_recomendacion(promedio_cal, promedio_prot, objetivo_cal, objetivo_prot):
    deficit_cal = objetivo_cal - promedio_prot; deficit_prot = objetivo_prot - promedio_prot
    sugerencias = {
        "alta_proteina_bajo_cal": ["Un yogur griego", "Una lata de atún al natural", "Un puñado de pavo en lonchas", "Un batido de proteínas con agua", "Claras de huevo revueltas"],
        "carbohidratos_energia": ["Una pieza de fruta", "Un puñado de avena con leche", "Una tostada de pan integral", "Un puñado de frutos secos"],
        "comida_completa": ["Pechuga de pollo a la plancha con arroz y brócoli", "Lentejas estofadas con verduras", "Salmón al horno con patata cocida"],
        "ligero": ["Una infusión o té", "Un vaso de agua con limón", "Un caldo de verduras bajo en sodio"]
    }
    if deficit_prot > 25 and deficit_cal > 400: return f"Necesitas una comida completa. ¿Qué tal: '{random.choice(sugerencias['comida_completa'])}'?"
    elif deficit_prot > 20: return f"Tu proteína está baja. Un snack rico en proteínas como '{random.choice(sugerencias['alta_proteina_bajo_cal'])}' sería ideal."
    elif deficit_cal > 350: return f"Necesitas energía. Algo como '{random.choice(sugerencias['carbohidratos_energia'])}' te sentaría genial."
    elif deficit_cal < -300: return f"Vas bien de energía. Si tienes hambre, opta por algo ligero como '{random.choice(sugerencias['ligero'])}'."
    else: return "¡Vas por buen camino! Tu ingesta promedio está bien alineada con tus objetivos. Sigue así."

# --- 3. CLASE PARA LA VENTANA DE APRENDIZAJE DE RECETAS ---
class RecipeConfirmationWindow(ctk.CTkToplevel):
    def __init__(self, parent, dish_name, found_ingredients):
        super().__init__(parent)
        self.title("Confirmar Ingredientes")
        self.geometry("500x400")
        self.transient(parent); self.grab_set()
        self.result = None
        main_label = ctk.CTkLabel(self, text=f"No conozco '{dish_name.title()}'.\nEdita la lista de ingredientes para que sea correcta:", font=ctk.CTkFont(size=16), wraplength=450)
        main_label.pack(pady=20, padx=20)
        self.ingredients_textbox = ctk.CTkTextbox(self, height=150, font=ctk.CTkFont(size=14))
        self.ingredients_textbox.pack(pady=10, padx=20, fill="both", expand=True)
        self.ingredients_textbox.insert("1.0", found_ingredients)
        button_frame = ctk.CTkFrame(self, fg_color="transparent"); button_frame.pack(pady=20)
        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel); cancel_button.pack(side="left", padx=10)
        confirm_button = ctk.CTkButton(button_frame, text="Confirmar y Guardar", command=self.confirm); confirm_button.pack(side="left", padx=10)
        self.wait_window()

    def confirm(self):
        self.result = self.ingredients_textbox.get("1.0", "end-1c").strip()
        if self.result: self.destroy()

    def cancel(self):
        self.result = None; self.destroy()

# --- 4. CLASE PRINCIPAL DE LA APLICACIÓN ---
class FitnessApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Asistente de Fitness Inteligente v2.4"); self.geometry("1300x850")
        self.objetivo_calorias = get_setting('objetivo_calorias') or 2200
        self.objetivo_proteinas = get_setting('objetivo_proteinas') or 150
        self.registros_diarios = cargar_datos_del_dia()
        self.notification_timer = None
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        main_container = ctk.CTkFrame(self, fg_color="transparent"); main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure(1, weight=1); main_container.grid_rowconfigure(0, weight=1)
        self.navigation_frame = ctk.CTkFrame(main_container, corner_radius=10); self.navigation_frame.grid(row=0, column=0, sticky="nsw")
        self.views_frame = ctk.CTkFrame(main_container, fg_color="transparent"); self.views_frame.grid(row=0, column=1, sticky="nsew", padx=(10,0))
        self.statusbar_frame = ctk.CTkFrame(self, height=30, corner_radius=0); self.statusbar_frame.grid(row=1, column=0, sticky="ew")
        self.notification_label = ctk.CTkLabel(self.statusbar_frame, text="", font=ctk.CTkFont(size=14)); self.notification_label.pack(side="left", padx=20)
        self.frame_registro_diario = ctk.CTkFrame(self.views_frame, fg_color="transparent")
        self.frame_seguimiento = ctk.CTkFrame(self.views_frame, fg_color="transparent")
        self.frame_ajustes = ctk.CTkFrame(self.views_frame, fg_color="transparent")
        self.frame_recomendaciones = ctk.CTkFrame(self.views_frame, fg_color="transparent")
        self.frame_mis_recetas = ctk.CTkFrame(self.views_frame, fg_color="transparent")
        self.crear_widgets_navegacion(); self.crear_vista_registro_diario(); self.crear_vista_seguimiento(); self.crear_vista_ajustes(); self.crear_vista_recomendaciones(); self.crear_vista_mis_recetas()
        self.seleccionar_vista("registro")

    # --- 4.1 Métodos de Lógica Interna y API ---
    def _show_notification(self, message, color):
        self.notification_label.configure(text=message, text_color=color)
        if self.notification_timer: self.after_cancel(self.notification_timer)
        self.notification_timer = self.after(5000, self._hide_notification)

    def _hide_notification(self):
        self.notification_label.configure(text=""); self.notification_timer = None
    
    def _search_recipe_ingredients_online(self, dish_name):
        self._show_notification(f"Buscando '{dish_name}' online (simulación)...", "cyan")
        if "fabada" in dish_name: return "200g fabes, 100g chorizo, 100g morcilla, 50g panceta"
        if "sushi" in dish_name: return "100g arroz de sushi, 50g salmon, alga nori"
        return None

    def _get_ingredients_for_dish(self, dish_name):
        ingredients = get_custom_recipe(dish_name)
        if ingredients:
            self._show_notification(f"Receta '{dish_name.title()}' encontrada en tu base de datos.", "cyan")
            return ingredients
        if dish_name in RECIPE_TRANSLATOR:
            self._show_notification(f"Receta '{dish_name.title()}' encontrada en el diccionario local.", "cyan")
            return RECIPE_TRANSLATOR[dish_name]
        found_ingredients = self._search_recipe_ingredients_online(dish_name)
        if found_ingredients:
            confirmation_window = RecipeConfirmationWindow(self, dish_name, found_ingredients)
            confirmed_ingredients = confirmation_window.result
            if confirmed_ingredients:
                save_custom_recipe(dish_name, confirmed_ingredients)
                self._show_notification(f"Nueva receta '{dish_name.title()}' guardada.", "#4CAF50")
                return confirmed_ingredients
        return None

    def _obtener_datos_nutricionales(self, texto_comida_original, is_complex_dish):
        if not APP_ID or APP_ID == "TU_ID_DE_NUTRITION_ANALYSIS":
            self._show_notification("Error: Configura tus credenciales de Edamam.", "red"); return None
        
        texto_lower = texto_comida_original.lower().strip()
        ingredientes_a_analizar = texto_lower
        
        if is_complex_dish:
            ingredients = self._get_ingredients_for_dish(texto_lower)
            if ingredients:
                ingredientes_a_analizar = ingredients
            else:
                self._show_notification(f"Registro de '{texto_lower.title()}' cancelado.", "#FFCC70")
                return None
        
        params = {"app_id": APP_ID, "app_key": APP_KEY}
        json_payload = {"ingr": ingredientes_a_analizar.split(',')}
        try:
            response = requests.post(DETAILS_API_URL, params=params, json=json_payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('totalNutrients'):
                calorias = round(data['totalNutrients'].get("ENERC_KCAL", {}).get('quantity', 0))
                proteinas = round(data['totalNutrients'].get("PROCNT", {}).get('quantity', 0))
                if calorias == 0 and proteinas == 0:
                    self._show_notification(f"No se pudo analizar '{texto_comida_original}'. Prueba a ser más específico.", "red"); return None
                return {"tipo": "Comida", "descripcion": texto_comida_original.capitalize(), "calorias": calorias, "proteinas": proteinas}
        except requests.exceptions.HTTPError:
            self._show_notification(f"Error de API al analizar '{texto_comida_original}'.", "red"); return None
        except requests.exceptions.RequestException:
            self._show_notification("Error de Conexión a la API de Edamam.", "red"); return None
        except Exception:
            self._show_notification(f"Error inesperado al procesar '{texto_comida_original}'.", "red"); return None
        return None
    
    # --- 4.2 Métodos de Construcción de la UI ---
    def crear_widgets_navegacion(self):
        self.btn_registro = ctk.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Registro Diario", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.seleccionar_vista("registro"))
        self.btn_registro.pack(pady=10, padx=10)
        self.btn_seguimiento = ctk.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Seguimiento", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.seleccionar_vista("seguimiento"))
        self.btn_seguimiento.pack(pady=10, padx=10)
        self.btn_recomendaciones = ctk.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Recomendaciones", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.seleccionar_vista("recomendaciones"))
        self.btn_recomendaciones.pack(pady=10, padx=10)
        self.btn_mis_recetas = ctk.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Mis Recetas", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.seleccionar_vista("mis_recetas"))
        self.btn_mis_recetas.pack(pady=10, padx=10)
        self.btn_ajustes = ctk.CTkButton(self.navigation_frame, corner_radius=10, height=40, border_spacing=10, text="Ajustes", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.seleccionar_vista("ajustes"))
        self.btn_ajustes.pack(pady=10, padx=10)

    def seleccionar_vista(self, nombre_vista):
        for frame in [self.frame_registro_diario, self.frame_seguimiento, self.frame_ajustes, self.frame_recomendaciones, self.frame_mis_recetas]: frame.grid_forget()
        for btn in [self.btn_registro, self.btn_seguimiento, self.btn_ajustes, self.btn_recomendaciones, self.btn_mis_recetas]: btn.configure(fg_color="transparent")
        if nombre_vista == "registro":
            self.frame_registro_diario.grid(row=0, column=0, sticky="nsew"); self.btn_registro.configure(fg_color=("gray75", "gray25"))
        elif nombre_vista == "seguimiento":
            self.frame_seguimiento.grid(row=0, column=0, sticky="nsew"); self.btn_seguimiento.configure(fg_color=("gray75", "gray25")); self.actualizar_vista_seguimiento()
        elif nombre_vista == "recomendaciones":
            self.frame_recomendaciones.grid(row=0, column=0, sticky="nsew"); self.btn_recomendaciones.configure(fg_color=("gray75", "gray25"))
        elif nombre_vista == "mis_recetas":
            self.frame_mis_recetas.grid(row=0, column=0, sticky="nsew"); self.btn_mis_recetas.configure(fg_color=("gray75", "gray25")); self.actualizar_vista_mis_recetas()
        elif nombre_vista == "ajustes":
            self.frame_ajustes.grid(row=0, column=0, sticky="nsew"); self.btn_ajustes.configure(fg_color=("gray75", "gray25")); self.cargar_ajustes_actuales()

    def crear_vista_registro_diario(self):
        self.frame_registro_diario.grid_columnconfigure(1, weight=3); self.frame_registro_diario.grid_columnconfigure(0, weight=1); self.frame_registro_diario.grid_rowconfigure(1, weight=1)
        dashboard_frame = ctk.CTkFrame(self.frame_registro_diario, height=100); dashboard_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,10)); dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.calorias_label = ctk.CTkLabel(dashboard_frame, font=ctk.CTkFont(size=20, weight="bold")); self.calorias_label.grid(row=0, column=0, pady=10)
        self.proteinas_label = ctk.CTkLabel(dashboard_frame, font=ctk.CTkFont(size=20, weight="bold")); self.proteinas_label.grid(row=0, column=1, pady=10)
        progress_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent"); progress_frame.grid(row=0, column=2, pady=10, padx=10); ctk.CTkLabel(progress_frame, text="Progreso de Calorías Diarias").pack()
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=250); self.progress_bar.pack(pady=5)
        self.progress_label = ctk.CTkLabel(progress_frame); self.progress_label.pack()
        sidebar_frame = ctk.CTkFrame(self.frame_registro_diario, width=300); sidebar_frame.grid(row=1, column=0, sticky="ns")
        tab_view = ctk.CTkTabview(sidebar_frame, width=280); tab_view.pack(pady=20, padx=10); tab_view.add("Nutrición"); tab_view.add("Ejercicio")
        
        nutrition_tab = tab_view.tab("Nutrición")
        self.comida_entry = ctk.CTkEntry(nutrition_tab, placeholder_text="Ej: 2 filetes de lomo adobado", width=250); self.comida_entry.pack(pady=10, padx=10); self.comida_entry.bind("<Return>", self.registrar_comida_evento)
        self.is_complex_dish_switch = ctk.CTkSwitch(nutrition_tab, text="Es una receta (buscar/aprender)", onvalue=True, offvalue=False)
        self.is_complex_dish_switch.pack(pady=10, padx=10)
        self.register_comida_button = ctk.CTkButton(nutrition_tab, text="Registrar Comida", command=self.registrar_comida_evento); self.register_comida_button.pack(pady=10)
        
        ejercicio_tab = tab_view.tab("Ejercicio"); self.ejercicio_tipo_combo = ctk.CTkComboBox(ejercicio_tab, values=["Fuerza", "Cardio", "Otro"], width=250); self.ejercicio_tipo_combo.pack(pady=10, padx=10)
        self.ejercicio_entry = ctk.CTkEntry(ejercicio_tab, placeholder_text="Descripción", width=250); self.ejercicio_entry.pack(pady=10, padx=10)
        self.duracion_entry = ctk.CTkEntry(ejercicio_tab, placeholder_text="Duración (minutos)", width=250); self.duracion_entry.pack(pady=10, padx=10)
        self.calorias_entry = ctk.CTkEntry(ejercicio_tab, placeholder_text="Calorías quemadas (opcional)", width=250); self.calorias_entry.pack(pady=10, padx=10); self.calorias_entry.bind("<Return>", self.registrar_ejercicio_evento)
        self.register_ejercicio_button = ctk.CTkButton(ejercicio_tab, text="Registrar Ejercicio", command=self.registrar_ejercicio_evento); self.register_ejercicio_button.pack(pady=10)
        main_frame = ctk.CTkFrame(self.frame_registro_diario); main_frame.grid(row=1, column=1, sticky="nsew", padx=(10,0))
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=28, fieldbackground="#2a2d2e", bordercolor="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=('Calibri', 13, 'bold'), relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        self.progress_table = ttk.Treeview(main_frame, columns=("Desc", "Cals", "Prot", "Dur"), show="headings");
        self.progress_table.heading("Desc", text="Descripción"); self.progress_table.heading("Cals", text="Calorías"); self.progress_table.heading("Prot", text="Proteína"); self.progress_table.heading("Dur", text="Duración (min)")
        self.progress_table.column("Desc", width=350); self.progress_table.column("Cals", anchor="center", width=100); self.progress_table.column("Prot", anchor="center", width=100); self.progress_table.column("Dur", anchor="center", width=120)
        self.progress_table.tag_configure('Comida', background='#3a543b'); self.progress_table.tag_configure('Ejercicio', background='#543a3a')
        self.progress_table.pack(fill="both", expand=True, padx=10, pady=10)
        self.actualizar_ui_registro_diario()

    def crear_vista_seguimiento(self):
        self.frame_seguimiento.grid_rowconfigure(1, weight=1); self.frame_seguimiento.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(self.frame_seguimiento, text="Análisis de Progreso", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=10)
        self.grafico_frame = ctk.CTkFrame(self.frame_seguimiento); self.grafico_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)
        stats_frame = ctk.CTkFrame(self.frame_seguimiento); stats_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.stats_label = ctk.CTkLabel(stats_frame, text="Calculando progreso...", font=ctk.CTkFont(size=14)); self.stats_label.pack(pady=10, padx=10)
        calendar_frame = ctk.CTkFrame(self.frame_seguimiento); calendar_frame.grid(row=2, column=1, sticky="nsew", padx=20, pady=10)
        ctk.CTkLabel(calendar_frame, text="Calendario de Cumplimiento (Últimos 30 días)", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.calendar_grid = ctk.CTkFrame(calendar_frame, fg_color="transparent"); self.calendar_grid.pack(pady=5)

    def crear_vista_ajustes(self):
        self.frame_ajustes.grid_columnconfigure(0, weight=1)
        
        # Frame de Objetivos
        goals_frame = ctk.CTkFrame(self.frame_ajustes); goals_frame.pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(goals_frame, text="Ajustes de Objetivos", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, anchor="w")
        ctk.CTkLabel(goals_frame, text="Objetivo de Calorías Diarias (kcal):").pack(anchor="w", padx=20)
        self.calorias_objetivo_entry = ctk.CTkEntry(goals_frame, width=200); self.calorias_objetivo_entry.pack(anchor="w", padx=20, pady=(0,10))
        ctk.CTkLabel(goals_frame, text="Objetivo de Proteínas Diarias (g):").pack(anchor="w", padx=20)
        self.proteinas_objetivo_entry = ctk.CTkEntry(goals_frame, width=200); self.proteinas_objetivo_entry.pack(anchor="w", padx=20, pady=(0,10))
        self.save_settings_button = ctk.CTkButton(goals_frame, text="Guardar Cambios", command=self.guardar_nuevos_ajustes); self.save_settings_button.pack(anchor="w", padx=20, pady=10)
        
        # Frame de Zona de Peligro
        danger_zone_frame = ctk.CTkFrame(self.frame_ajustes, fg_color="#424242"); danger_zone_frame.pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(danger_zone_frame, text="Zona de Peligro", font=ctk.CTkFont(size=16, weight="bold"), text_color="#F44336").pack(pady=10, anchor="w")
        ctk.CTkLabel(danger_zone_frame, text="Esta acción borrará permanentemente todo tu historial de comidas y ejercicios.", wraplength=800).pack(anchor="w", padx=20)
        self.btn_delete_history = ctk.CTkButton(danger_zone_frame, text="Borrar Historial de Registros", command=self.delete_log_data_event, fg_color="#D32F2F", hover_color="#B71C1C"); self.btn_delete_history.pack(anchor="w", padx=20, pady=10)

    def crear_vista_recomendaciones(self):
        self.frame_recomendaciones.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.frame_recomendaciones, text="Asistente de Comidas", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20, padx=20)
        ctk.CTkLabel(self.frame_recomendaciones, text="Analiza mi ingesta de los últimos días y sugiéreme qué podría comer ahora.", wraplength=600).pack(pady=10, padx=20)
        ctk.CTkButton(self.frame_recomendaciones, text="¡Dame una idea!", command=self.actualizar_recomendacion, height=40).pack(pady=30, padx=20)
        self.recomendacion_resultado_label = ctk.CTkLabel(self.frame_recomendaciones, text="", font=ctk.CTkFont(size=16), wraplength=700, justify="center")
        self.recomendacion_resultado_label.pack(pady=20, padx=20)
    
    def crear_vista_mis_recetas(self):
        self.frame_mis_recetas.grid_columnconfigure(1, weight=2); self.frame_mis_recetas.grid_rowconfigure(1, weight=1)
        left_frame = ctk.CTkFrame(self.frame_mis_recetas); left_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew"); left_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(left_frame, text="Recetas Guardadas", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10)
        self.recipe_listbox = ctk.CTkScrollableFrame(left_frame); self.recipe_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        right_frame = ctk.CTkFrame(self.frame_mis_recetas); right_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew"); right_frame.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(right_frame, text="Editor de Recetas", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        ctk.CTkLabel(right_frame, text="Nombre del Plato:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.recipe_name_entry = ctk.CTkEntry(right_frame, width=300); self.recipe_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(right_frame, text="Ingredientes (separados por comas):").grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        self.recipe_ingredients_textbox = ctk.CTkTextbox(right_frame); self.recipe_ingredients_textbox.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
        button_frame = ctk.CTkFrame(right_frame, fg_color="transparent"); button_frame.grid(row=3, column=1, pady=10, padx=10, sticky="e")
        self.btn_clear_recipe = ctk.CTkButton(button_frame, text="Nuevo", command=self.clear_recipe_editor); self.btn_clear_recipe.pack(side="left", padx=5)
        self.btn_delete_recipe = ctk.CTkButton(button_frame, text="Eliminar", command=self.delete_recipe_event, fg_color="#D32F2F", hover_color="#B71C1C"); self.btn_delete_recipe.pack(side="left", padx=5)
        self.btn_save_recipe = ctk.CTkButton(button_frame, text="Guardar", command=self.save_recipe_event); self.btn_save_recipe.pack(side="left", padx=5)

    # --- 4.3 Métodos de Eventos y Actualización de UI ---
    def actualizar_recomendacion(self):
        analisis = obtener_promedio_nutrientes(dias=3)
        if analisis["dias_registrados"] < 2:
            self._show_notification("Necesito al menos 2 días de registros para dar una recomendación.", "#FFCC70"); return
        texto_analisis = f"Análisis basado en los últimos {analisis['dias_registrados']} días:\nPromedio de Calorías: {round(analisis['promedio_cal'])} kcal | Promedio de Proteínas: {round(analisis['promedio_prot'])} g"
        sugerencia = generar_recomendacion(analisis["promedio_cal"], analisis["promedio_prot"], self.objetivo_calorias, self.objetivo_proteinas)
        self.recomendacion_resultado_label.configure(text=sugerencia)

    def guardar_nuevos_ajustes(self):
        try:
            nuevo_obj_cal = float(self.calorias_objetivo_entry.get()); nuevo_obj_prot = float(self.proteinas_objetivo_entry.get())
            save_setting('objetivo_calorias', nuevo_obj_cal); save_setting('objetivo_proteinas', nuevo_obj_prot)
            self.objetivo_calorias = nuevo_obj_cal; self.objetivo_proteinas = nuevo_obj_prot
            self._show_notification("✓ Cambios guardados correctamente", "#4CAF50"); self.actualizar_ui_registro_diario()
        except ValueError: self._show_notification("Error: Los valores de los objetivos deben ser números.", "red")
    
    def delete_log_data_event(self): # NUEVO
        confirmed = messagebox.askyesno(
            "Confirmar Borrado de Datos",
            "Atención: ¿Estás seguro de que quieres borrar TODO tu historial de comidas y ejercicios?\n\nEsta acción no se puede deshacer.\n\nTus recetas personalizadas y objetivos NO se borrarán.",
            icon="warning"
        )
        if confirmed:
            delete_all_log_data()
            self.registros_diarios.clear()
            self.actualizar_ui_registro_diario()
            self._show_notification("✓ Historial de registros borrado correctamente.", "#4CAF50")

    def registrar_comida_evento(self, event=None):
        texto = self.comida_entry.get()
        is_complex = self.is_complex_dish_switch.get()
        if not texto: self._show_notification("El campo de comida no puede estar vacío.", "#FFCC70"); return
        datos = self._obtener_datos_nutricionales(texto, is_complex)
        if datos: guardar_registro_en_db(datos); self.registros_diarios.append(datos); self.actualizar_ui_registro_diario(); self.comida_entry.delete(0, 'end')

    def registrar_ejercicio_evento(self, event=None):
        tipo_ej, desc, dur_str, cals_str = self.ejercicio_tipo_combo.get(), self.ejercicio_entry.get(), self.duracion_entry.get(), self.calorias_entry.get()
        if not desc or not dur_str: self._show_notification("La descripción y la duración del ejercicio son obligatorias.", "#FFCC70"); return
        try: duracion = int(dur_str); cal_quemadas = -abs(int(cals_str)) if cals_str else 0
        except ValueError: self._show_notification("Error: La duración y las calorías deben ser números.", "red"); return
        reg = {"tipo": "Ejercicio", "descripcion": desc, "calorias": cal_quemadas, "proteinas": None, "ejercicio_tipo": tipo_ej, "duracion_min": duracion}
        guardar_registro_en_db(reg); self.registros_diarios.append(reg); self.actualizar_ui_registro_diario()
        self.ejercicio_entry.delete(0, 'end'); self.duracion_entry.delete(0, 'end'); self.calorias_entry.delete(0, 'end')

    def actualizar_ui_registro_diario(self):
        for i in self.progress_table.get_children(): self.progress_table.delete(i)
        netas, consumidas, proteinas = 0, 0, 0
        for reg in self.registros_diarios:
            duracion_display = reg.get('duracion_min') or "---"; self.progress_table.insert("", "end", values=(reg["descripcion"], reg["calorias"], reg["proteinas"], duracion_display), tags=(reg["tipo"],))
            netas += reg["calorias"];
            if reg["tipo"] == "Comida": proteinas += reg["proteinas"]; consumidas += reg["calorias"]
        self.calorias_label.configure(text=f"{round(netas)}\nCalorías Netas"); self.proteinas_label.configure(text=f"{round(proteinas)} g\nProteínas")
        progreso = consumidas / self.objetivo_calorias if self.objetivo_calorias > 0 else 0; self.progress_bar.set(progreso if progreso > 0 else 0)
        self.progress_label.configure(text=f"{round(consumidas)} / {self.objetivo_calorias} kcal")

    def actualizar_vista_seguimiento(self): self.actualizar_graficas(); self.actualizar_stats_y_calendario()

    def actualizar_graficas(self):
        for widget in self.grafico_frame.winfo_children(): widget.destroy()
        datos = obtener_datos_historicos(dias=7)
        if not any(datos["calorias_netas"]): ctk.CTkLabel(self.grafico_frame, text="No hay datos para la gráfica.").pack(pady=100); return
        plt.style.use('dark_background'); fig, ax1 = plt.subplots(figsize=(12, 6)); colores = ['#4CAF50' if cal <= datos['objetivo_calorias'] else '#F44336' for cal in datos['calorias_netas']]
        ax1.bar(datos["fechas_labels"], datos["calorias_netas"], color=colores, label='Calorías Netas'); ax1.axhline(y=datos['objetivo_calorias'], color='yellow', linestyle='--', label=f'Objetivo ({datos["objetivo_calorias"]} kcal)'); ax1.set_ylabel('Calorías Netas (kcal)', color='w'); ax1.tick_params(axis='y', labelcolor='w'); ax1.tick_params(axis='x', labelrotation=45, colors='w'); ax1.legend(loc='upper left')
        ax2 = ax1.twinx(); ax2.plot(datos["fechas_labels"], datos["proteinas"], color='#2196F3', marker='o', label='Proteínas'); ax2.set_ylabel('Proteínas (g)', color='#2196F3'); ax2.tick_params(axis='y', labelcolor='#2196F3'); ax2.legend(loc='upper right'); fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)

    def actualizar_stats_y_calendario(self):
        datos = obtener_datos_historicos(dias=30)
        if datos['calorias_netas']:
            calorias_consumidas = [c for c in datos['calorias_netas'] if c > 0]
            if calorias_consumidas:
                deficit_promedio = sum(c - datos['objetivo_calorias'] for c in calorias_consumidas) / len(calorias_consumidas)
                perdida_semanal_kg = (deficit_promedio * 7) / 7700; texto_stats = f"Déficit diario promedio: {round(deficit_promedio)} kcal → Pérdida de peso estimada: {perdida_semanal_kg:.2f} kg/semana"
            else: texto_stats = "No hay datos de consumo para calcular progreso."
        else: texto_stats = "Registra más días para ver tu progreso estimado."
        self.stats_label.configure(text=texto_stats);
        for widget in self.calendar_grid.winfo_children(): widget.destroy()
        dias_cumplidos = [c <= datos['objetivo_calorias'] and c > 0 for c in datos['calorias_netas']]
        for i, cumplido in enumerate(reversed(dias_cumplidos)):
            dia_label = date.today() - timedelta(days=i); color = "#4CAF50" if cumplido else "#F44336"
            dia_widget = ctk.CTkLabel(self.calendar_grid, text=dia_label.strftime('%d'), fg_color=color, width=30, height=30, corner_radius=5); dia_widget.grid(row=(i // 7), column=(i % 7), padx=2, pady=2)

    def cargar_ajustes_actuales(self):
        self.calorias_objetivo_entry.delete(0, 'end'); self.calorias_objetivo_entry.insert(0, str(self.objetivo_calorias))
        self.proteinas_objetivo_entry.delete(0, 'end'); self.proteinas_objetivo_entry.insert(0, str(self.objetivo_proteinas))
    
    def actualizar_vista_mis_recetas(self):
        for widget in self.recipe_listbox.winfo_children(): widget.destroy()
        recipes = get_all_custom_recipes()
        for name, ingredients in recipes:
            btn = ctk.CTkButton(self.recipe_listbox, text=name.title(), fg_color="transparent", anchor="w",
                                command=lambda n=name, i=ingredients: self.select_recipe_for_editing(n, i))
            btn.pack(fill="x", padx=5, pady=2)
        self.clear_recipe_editor()

    def select_recipe_for_editing(self, name, ingredients):
        self.recipe_name_entry.delete(0, "end"); self.recipe_name_entry.insert(0, name.title())
        self.recipe_ingredients_textbox.delete("1.0", "end"); self.recipe_ingredients_textbox.insert("1.0", ingredients)

    def save_recipe_event(self):
        name = self.recipe_name_entry.get().strip()
        ingredients = self.recipe_ingredients_textbox.get("1.0", "end-1c").strip()
        if not name or not ingredients:
            self._show_notification("El nombre y los ingredientes no pueden estar vacíos.", "#FFCC70"); return
        save_custom_recipe(name, ingredients)
        self._show_notification(f"Receta '{name.title()}' guardada.", "#4CAF50")
        self.actualizar_vista_mis_recetas()

    def delete_recipe_event(self):
        name = self.recipe_name_entry.get().strip()
        if not name:
            self._show_notification("Selecciona una receta para eliminar.", "#FFCC70"); return
        delete_custom_recipe(name)
        self._show_notification(f"Receta '{name.title()}' eliminada.", "#4CAF50")
        self.actualizar_vista_mis_recetas()

    def clear_recipe_editor(self):
        self.recipe_name_entry.delete(0, "end")
        self.recipe_ingredients_textbox.delete("1.0", "end")
        self.recipe_name_entry.focus()
    
if __name__ == "__main__":
    init_db()
    app = FitnessApp()
    app.mainloop()
