import customtkinter as ctk
import requests
from tkinter import ttk, messagebox
import sqlite3
from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# --- CONFIGURACIÓN Y BASE DE DATOS ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

EDAMAM_APP_ID = "Tu_app_ID"
EDAMAM_APP_KEY = "Tu_app_key"
NUTRITION_API_URL = f"https://api.edamam.com/api/nutrition-details?app_id={EDAMAM_APP_ID}&app_key={EDAMAM_APP_KEY}"
DB_FILE = "fitness_data.db"

# --- FUNCIONES DE BASE DE DATOS Y API ---

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
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('objetivo_calorias', 2200)")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('objetivo_proteinas', 150)")
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

def obtener_datos_nutricionales(texto_comida):
    if not EDAMAM_APP_ID or EDAMAM_APP_ID == "TU_APP_ID":
        messagebox.showerror("Error", "Configura tus credenciales de la API de Edamam."); return None
    texto_normalizado = texto_comida.lower().strip()
    headers, data = {'Content-Type': 'application/json'}, {"ingr": texto_normalizado.split(',')}
    try:
        response = requests.post(NUTRITION_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        api_data = response.json(); total_nutrients = api_data.get("totalNutrients", {})
        calorias = round(total_nutrients.get("ENERC_KCAL", {}).get("quantity", 0))
        proteinas = round(total_nutrients.get("PROCNT", {}).get("quantity", 0))
        return {"tipo": "Comida", "descripcion": texto_comida.capitalize(), "calorias": calorias, "proteinas": proteinas}
    except requests.exceptions.HTTPError:
        messagebox.showwarning("No Encontrado", f"No se pudo analizar: '{texto_comida}'."); return None
    except requests.exceptions.RequestException:
        messagebox.showerror("Error de Conexión", "No se pudo conectar a la API."); return None
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}"); return None

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
    deficit_cal = objetivo_cal - promedio_cal; deficit_prot = objetivo_prot - promedio_prot
    sugerencias = {
        "alta_proteina_bajo_cal": ["Un yogur griego", "Una lata de atún al natural", "Un puñado de pavo en lonchas", "Un batido de proteínas con agua", "Claras de huevo revueltas"],
        "carbohidratos_energia": ["Una pieza de fruta (manzana, plátano)", "Un puñado de avena con agua o leche", "Una tostada de pan integral con aceite", "Un puñado de dátiles o frutos secos"],
        "comida_completa": ["Pechuga de pollo a la plancha con arroz y brócoli", "Lentejas estofadas con verduras", "Salmón al horno con patata cocida", "Revuelto de huevos con espinacas y una rebanada de pan integral"],
        "ligero": ["Una infusión o té", "Un vaso de agua con limón", "Un caldo de verduras bajo en sodio", "Unos pepinillos o encurtidos"]
    }
    if deficit_prot > 25 and deficit_cal > 400: return f"Parece que necesitas una comida completa. ¿Qué tal algo como '{random.choice(sugerencias['comida_completa'])}'?"
    elif deficit_prot > 20: return f"Tu proteína está un poco baja. Un snack rico en proteínas como '{random.choice(sugerencias['alta_proteina_bajo_cal'])}' sería ideal."
    elif deficit_cal > 350: return f"Necesitas un extra de energía. Algo como '{random.choice(sugerencias['carbohidratos_energia'])}' te sentaría genial."
    elif deficit_cal < -300: return f"Vas bien de energía. Si tienes hambre, opta por algo ligero como '{random.choice(sugerencias['ligero'])}' para no pasarte."
    else: return "¡Vas por el buen camino! Tu ingesta promedio está bien alineada con tus objetivos. Sigue así."

class FitnessApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Asistente de Fitness Definitivo"); self.geometry("1300x850")
        self.objetivo_calorias = get_setting('objetivo_calorias') or 2200
        self.objetivo_proteinas = get_setting('objetivo_proteinas') or 150
        self.registros_diarios = cargar_datos_del_dia()
        self.save_notification_timer = None
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0); self.navigation_frame.grid(row=0, column=0, sticky="nsw")
        self.frame_registro_diario = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_seguimiento = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_ajustes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_recomendaciones = ctk.CTkFrame(self, fg_color="transparent")
        self.crear_widgets_navegacion()
        self.crear_vista_registro_diario()
        self.crear_vista_seguimiento()
        self.crear_vista_ajustes()
        self.crear_vista_recomendaciones()
        self.seleccionar_vista("registro")

    def crear_widgets_navegacion(self):
        self.btn_registro = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Registro Diario", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.seleccionar_vista("registro"))
        self.btn_registro.pack(pady=20, padx=20)
        self.btn_seguimiento = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Seguimiento", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.seleccionar_vista("seguimiento"))
        self.btn_seguimiento.pack(pady=10, padx=20)
        self.btn_recomendaciones = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Recomendaciones", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.seleccionar_vista("recomendaciones"))
        self.btn_recomendaciones.pack(pady=10, padx=20)
        self.btn_ajustes = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Ajustes", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.seleccionar_vista("ajustes"))
        self.btn_ajustes.pack(pady=10, padx=20)

    def seleccionar_vista(self, nombre_vista):
        for frame in [self.frame_registro_diario, self.frame_seguimiento, self.frame_ajustes, self.frame_recomendaciones]: frame.grid_forget()
        for btn in [self.btn_registro, self.btn_seguimiento, self.btn_ajustes, self.btn_recomendaciones]: btn.configure(fg_color="transparent")
        if nombre_vista == "registro":
            self.frame_registro_diario.grid(row=0, column=1, sticky="nsew", padx=20, pady=20); self.btn_registro.configure(fg_color=("gray75", "gray25"))
        elif nombre_vista == "seguimiento":
            self.frame_seguimiento.grid(row=0, column=1, sticky="nsew", padx=20, pady=20); self.btn_seguimiento.configure(fg_color=("gray75", "gray25")); self.actualizar_vista_seguimiento()
        elif nombre_vista == "recomendaciones":
            self.frame_recomendaciones.grid(row=0, column=1, sticky="nsew", padx=20, pady=20); self.btn_recomendaciones.configure(fg_color=("gray75", "gray25"))
        elif nombre_vista == "ajustes":
            self.frame_ajustes.grid(row=0, column=1, sticky="nsew", padx=20, pady=20); self.btn_ajustes.configure(fg_color=("gray75", "gray25")); self.cargar_ajustes_actuales()

    def crear_vista_registro_diario(self):
        self.frame_registro_diario.grid_columnconfigure(1, weight=3); self.frame_registro_diario.grid_columnconfigure(0, weight=1); self.frame_registro_diario.grid_rowconfigure(1, weight=1)
        dashboard_frame = ctk.CTkFrame(self.frame_registro_diario, height=100); dashboard_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,20)); dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.calorias_label = ctk.CTkLabel(dashboard_frame, font=ctk.CTkFont(size=20, weight="bold")); self.calorias_label.grid(row=0, column=0, pady=10)
        self.proteinas_label = ctk.CTkLabel(dashboard_frame, font=ctk.CTkFont(size=20, weight="bold")); self.proteinas_label.grid(row=0, column=1, pady=10)
        progress_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent"); progress_frame.grid(row=0, column=2, pady=10, padx=10); ctk.CTkLabel(progress_frame, text="Progreso de Calorías Diarias").pack()
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=250); self.progress_bar.pack(pady=5)
        self.progress_label = ctk.CTkLabel(progress_frame); self.progress_label.pack()
        sidebar_frame = ctk.CTkFrame(self.frame_registro_diario, width=300); sidebar_frame.grid(row=1, column=0, sticky="ns")
        tab_view = ctk.CTkTabview(sidebar_frame, width=280); tab_view.pack(pady=20, padx=10); tab_view.add("Nutrición"); tab_view.add("Ejercicio")
        self.comida_entry = ctk.CTkEntry(tab_view.tab("Nutrición"), placeholder_text="Ej: 200g pechuga de pollo", width=250); self.comida_entry.pack(pady=15, padx=10); self.comida_entry.bind("<Return>", self.registrar_comida_evento)
        self.register_comida_button = ctk.CTkButton(tab_view.tab("Nutrición"), text="Registrar Comida", command=self.registrar_comida_evento); self.register_comida_button.pack(pady=10)
        ejercicio_tab = tab_view.tab("Ejercicio"); self.ejercicio_tipo_combo = ctk.CTkComboBox(ejercicio_tab, values=["Fuerza", "Cardio", "Otro"], width=250); self.ejercicio_tipo_combo.pack(pady=10, padx=10)
        self.ejercicio_entry = ctk.CTkEntry(ejercicio_tab, placeholder_text="Descripción", width=250); self.ejercicio_entry.pack(pady=10, padx=10)
        self.duracion_entry = ctk.CTkEntry(ejercicio_tab, placeholder_text="Duración (minutos)", width=250); self.duracion_entry.pack(pady=10, padx=10)
        self.calorias_entry = ctk.CTkEntry(ejercicio_tab, placeholder_text="Calorías quemadas (opcional)", width=250); self.calorias_entry.pack(pady=10, padx=10); self.calorias_entry.bind("<Return>", self.registrar_ejercicio_evento)
        self.register_ejercicio_button = ctk.CTkButton(ejercicio_tab, text="Registrar Ejercicio", command=self.registrar_ejercicio_evento); self.register_ejercicio_button.pack(pady=10)
        main_frame = ctk.CTkFrame(self.frame_registro_diario); main_frame.grid(row=1, column=1, sticky="nsew", padx=20)
        style = ttk.Style(); style.configure("Treeview", font=('Calibri', 11), rowheight=28, background="#2a2d2e", foreground="white", fieldbackground="#343638"); style.map('Treeview', background=[('selected', '#22559b')]); style.configure("Treeview.Heading", font=('Calibri', 13, 'bold'), background="#565b5e", foreground="white")
        self.progress_table = ttk.Treeview(main_frame, columns=("Desc", "Cals", "Prot", "Dur"), show="headings"); self.progress_table.heading("Desc", text="Descripción"); self.progress_table.heading("Cals", text="Calorías"); self.progress_table.heading("Prot", text="Proteína"); self.progress_table.heading("Dur", text="Duración (min)")
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
        ctk.CTkLabel(self.frame_ajustes, text="Ajustes de Objetivos", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=50, pady=20)
        ctk.CTkLabel(self.frame_ajustes, text="Objetivo de Calorías Diarias (kcal):").grid(row=1, column=0, padx=50, pady=(10,0), sticky="w")
        self.calorias_objetivo_entry = ctk.CTkEntry(self.frame_ajustes, width=200); self.calorias_objetivo_entry.grid(row=2, column=0, padx=50, pady=(0,20), sticky="w")
        ctk.CTkLabel(self.frame_ajustes, text="Objetivo de Proteínas Diarias (g):").grid(row=3, column=0, padx=50, pady=(10,0), sticky="w")
        self.proteinas_objetivo_entry = ctk.CTkEntry(self.frame_ajustes, width=200); self.proteinas_objetivo_entry.grid(row=4, column=0, padx=50, pady=(0,20), sticky="w")
        self.save_settings_button = ctk.CTkButton(self.frame_ajustes, text="Guardar Cambios", command=self.guardar_nuevos_ajustes); self.save_settings_button.grid(row=5, column=0, padx=50, pady=30, sticky="w")
        self.save_confirmation_label = ctk.CTkLabel(self.frame_ajustes, text=" ✓ Cambios guardados", text_color="#4CAF50", font=ctk.CTkFont(size=14, weight="bold"))

    def crear_vista_recomendaciones(self):
        self.frame_recomendaciones.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.frame_recomendaciones, text="Asistente de Comidas", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20, padx=20)
        ctk.CTkLabel(self.frame_recomendaciones, text="Analiza mi ingesta de los últimos días y sugiéreme qué podría comer ahora.", wraplength=600).pack(pady=10, padx=20)
        ctk.CTkButton(self.frame_recomendaciones, text="¡Dame una idea!", command=self.actualizar_recomendacion, height=40).pack(pady=30, padx=20)
        self.recomendacion_resultado_label = ctk.CTkLabel(self.frame_recomendaciones, text="", font=ctk.CTkFont(size=16), wraplength=700, justify="center")
        self.recomendacion_resultado_label.pack(pady=20, padx=20)

    def actualizar_recomendacion(self):
        analisis = obtener_promedio_nutrientes(dias=3)
        if analisis["dias_registrados"] < 2:
            self.recomendacion_resultado_label.configure(text="Necesito al menos 2 días de registros para darte una buena recomendación. ¡Sigue apuntando lo que comes!")
            return
        texto_analisis = f"Análisis basado en los últimos {analisis['dias_registrados']} días:\nPromedio de Calorías: {round(analisis['promedio_cal'])} kcal | Promedio de Proteínas: {round(analisis['promedio_prot'])} g"
        sugerencia = generar_recomendacion(analisis["promedio_cal"], analisis["promedio_prot"], self.objetivo_calorias, self.objetivo_proteinas)
        self.recomendacion_resultado_label.configure(text=f"{texto_analisis}\n\n{sugerencia}")

    def guardar_nuevos_ajustes(self):
        try:
            nuevo_obj_cal = float(self.calorias_objetivo_entry.get()); nuevo_obj_prot = float(self.proteinas_objetivo_entry.get())
            save_setting('objetivo_calorias', nuevo_obj_cal); save_setting('objetivo_proteinas', nuevo_obj_prot)
            self.objetivo_calorias = nuevo_obj_cal; self.objetivo_proteinas = nuevo_obj_prot
            self.mostrar_notificacion_guardado(); self.actualizar_ui_registro_diario()
        except ValueError: messagebox.showerror("Error", "Los valores deben ser números válidos.")

    def mostrar_notificacion_guardado(self):
        self.save_confirmation_label.grid(row=6, column=0, padx=50, pady=10, sticky="w")
        if self.save_notification_timer is not None: self.after_cancel(self.save_notification_timer)
        self.save_notification_timer = self.after(3000, self.ocultar_notificacion_guardado)

    def ocultar_notificacion_guardado(self):
        self.save_confirmation_label.grid_forget(); self.save_notification_timer = None

    def registrar_comida_evento(self, event=None):
        texto = self.comida_entry.get();
        if not texto: return
        datos = obtener_datos_nutricionales(texto)
        if datos: guardar_registro_en_db(datos); self.registros_diarios.append(datos); self.actualizar_ui_registro_diario(); self.comida_entry.delete(0, 'end')

    def registrar_ejercicio_evento(self, event=None):
        tipo_ej, desc, dur_str, cals_str = self.ejercicio_tipo_combo.get(), self.ejercicio_entry.get(), self.duracion_entry.get(), self.calorias_entry.get()
        if not desc or not dur_str: messagebox.showwarning("Campos Requeridos", "La descripción y la duración son obligatorias."); return
        try: duracion = int(dur_str); cal_quemadas = -abs(int(cals_str)) if cals_str else 0
        except ValueError: messagebox.showerror("Error", "La duración y las calorías deben ser números."); return
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

if __name__ == "__main__":
    init_db()
    app = FitnessApp()
    app.mainloop()
