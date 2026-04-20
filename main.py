import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import sqlite3
import pandas as pd
import re
import os
import random
import requests
import json
import webbrowser
from datetime import datetime, timedelta
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =============================================================================
# 1. ARQUITECTURA GLOBAL Y PROTOCOLOS DE SEGURIDAD
# =============================================================================
# Definimos las constantes que rigen el comportamiento del sistema.
# Estas variables son el corazón de la configuración de Sentinel Omega.
COMUNA_ACTUAL = "SAN BERNARDO"
VERSION = "0.1.1 - SENTINEL OMEGA (MASTER PIECE)"
DB_NAME = "sentinel_omega.db"
PIN_DESBLOQUEO = "12345"
ADMIN_CLAVE = "duoc2026"

# Paleta de Colores Tácticos (Unificada para consistencia visual y psicológica)
HEX_ROJO = "#FF0000"     # Código Rojo: Emergencias letales e inmediatas
HEX_MORADO = "#800080"   # Crítico: Riesgo vital, accidentes o temas médicos
HEX_NARANJA = "#FF8C00"  # Alto: Delincuencia activa o amenazas de violencia
HEX_AZUL = "#0000FF"     # Moderado: Alteración del orden o ruidos molestos
HEX_CELESTE = "#87CEEB"  # Bajo: Informativo, preventivo o dudas generales
HEX_FONDO = "#050505"    # Negro profundo para estética tech y ahorro de energía
HEX_TEXTO_IA = "#00FF00" # Verde Matriz para el área de escritura del usuario

def inicializar_entorno():
    """Garantiza que el sistema tenga la infraestructura de carpetas necesaria."""
    # Sentinel necesita organizar sus actas, reportes y respaldos de datos.
    carpetas = ["REPORTES_PDF", "EXPORTS", "BACKUPS", "LOGS"]
    for c in carpetas:
        if not os.path.exists(c):
            os.makedirs(c)

def obtener_geolocalizacion_real():
    """Rastreo de ubicación para validez institucional del reporte vía IP."""
    # Esto añade una capa de veracidad a los reportes generados por los alumnos.
    try:
        r = requests.get('https://ipapi.co/json/', timeout=2)
        if r.status_code == 200:
            d = r.json()
            return f"{d.get('city', 'S.B')}, {d.get('region', 'R.M')} | LAT: {d.get('latitude')}, LON: {d.get('longitude')}"
    except:
        pass
    # Si falla el internet, devolvemos la ubicación base de la sede.
    return f"{COMUNA_ACTUAL}, CHILE (UBICACIÓN ESTIMADA SEDE)"

# =============================================================================
# 2. MOTOR DE ANÁLISIS DE RIESGO (INTELIGENCIA LINGÜÍSTICA)
# =============================================================================
class MotorAnalisis:
    """Clase encargada de filtrar y categorizar el lenguaje del usuario en tiempo real."""
    @staticmethod
    def clasificar(texto):
        t = texto.lower()
        
        # PRIORIDAD MÁXIMA: CÓDIGO ROJO (Protocolos de evacuación inmediata)
        # Buscamos patrones de armas, incendios o explosivos.
        if re.search(r"(bomba|explosivo|dinamita|granada|paquete|fuego|incendio|humo|gas|explosion|tiroteo|balacera|pistola|arma|disparo|tirador|fusil)", t):
            return "CÓDIGO ROJO", 1000

        # NIVEL: CRÍTICO (Riesgo directo a la integridad física y vida)
        if re.search(r"(matar|morir|sangre|herido|apuñalado|sicario|degollado|fallecido|infarto|desmayo|ambulancia|muerte)", t):
            return "CRÍTICO", 500
            
        # NIVEL: ALTO (Delincuencia y seguridad ciudadana activa)
        if re.search(r"(pegar|golpe|funa|amenaza|robo|encerrona|portonazo|asalto|ladrón|delincuente|asaltar|quitada)", t):
            return "ALTO", 300
            
        # NIVEL: MODERADO (Convivencia, ruidos y consumo de sustancias)
        if re.search(r"(grito|pelea|insulto|sospechoso|tussi|drogas|alcohol|ebrio|droga|marihuana|vicio)", t):
            return "MODERADO", 150
            
        # Por defecto, si no hay palabras clave, el riesgo se considera bajo.
        return "BAJO", 50

# =============================================================================
# 3. GESTIÓN DE DATOS (PERSISTENCIA Y SEGURIDAD SQLITE)
# =============================================================================
class Database:
    """Maneja la base de datos para que ningún reporte se pierda, incluso tras un cierre."""
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.crear_tablas()

    def crear_tablas(self):
        """Define la estructura de la tabla de reportes institucionales."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reportes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                contenido TEXT,
                nivel_riesgo TEXT,
                puntaje INTEGER,
                folio TEXT,
                estado TEXT,
                ubicacion TEXT,
                rol_emisor TEXT,
                fecha_resolucion TEXT
            )
        """)
        self.conn.commit()

    def insertar(self, contenido, riesgo, pts, folio, rol, geo):
        """Registra un nuevo incidente en la base de datos."""
        self.cursor.execute("""
            INSERT INTO reportes (fecha, contenido, nivel_riesgo, puntaje, folio, estado, ubicacion, rol_emisor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), contenido, riesgo, pts, folio, "ACTIVO", geo, rol))
        self.conn.commit()

    def purga_7_dias(self):
        """Lógica de autolimpieza para proteger la privacidad y optimizar espacio."""
        fecha_limite = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        self.cursor.execute("DELETE FROM reportes WHERE estado='FINALIZADO' AND date(fecha_resolucion) <= ?", (fecha_limite,))
        self.conn.commit()

# =============================================================================
# 4. GENERADOR DE DOCUMENTACIÓN (ACTA INSTITUCIONAL PDF)
# =============================================================================
class GeneradorActa(FPDF):
    """Crea documentos formales que pueden ser entregados a las autoridades."""
    def header(self):
        # Dibujamos un marco estético y profesional para el documento.
        self.rect(5, 5, 200, 287)
        self.set_fill_color(20, 20, 20)
        self.rect(5, 5, 200, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", 'B', 16)
        self.cell(0, 15, "SENTINEL OMEGA - ACTA DE INCIDENTE OFICIAL", ln=True, align='C')
        self.set_font("Arial", 'I', 9)
        self.cell(0, 5, f"SISTEMA DE RESPUESTA Y VIGILANCIA - SEDE {COMUNA_ACTUAL}", ln=True, align='C')
        self.ln(25)

    def footer(self):
        # Espacio para firmas y timbres legales.
        self.set_y(-50)
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", 'B', 10)
        self.cell(90, 10, "__________________________", 0, 0, 'C')
        self.cell(90, 10, "__________________________", 0, 1, 'C')
        self.cell(90, 5, "FIRMA DEL OPERADOR", 0, 0, 'C')
        self.cell(90, 5, "TIMBRE DE RECEPCIÓN", 0, 1, 'C')

# =============================================================================
# 5. APLICACIÓN CORE (SENTINEL OMEGA USER INTERFACE)
# =============================================================================
class SentinelOmegaApp:
    """La interfaz principal donde ocurre la magia de la protección."""
    def __init__(self, root):
        self.root = root
        self.db = Database()
        inicializar_entorno()
        self.db.purga_7_dias() # Limpieza automática al iniciar
        
        self.root.title(f"SENTINEL OMEGA v{VERSION}")
        self.root.geometry("1000x950")
        self.root.configure(bg=HEX_FONDO)
        
        # El contenedor nos permite cambiar de "pantalla" sin cerrar la ventana.
        self.container = tk.Frame(self.root, bg=HEX_FONDO)
        self.container.pack(expand=True, fill="both")
        
        self.pantalla_inicio()

    def pantalla_inicio(self):
        """Configuración de la vista principal con enfoque en la calma del usuario."""
        for w in self.container.winfo_children(): w.destroy()
        
        # Logotipo y Lema Amigable
        tk.Label(self.container, text="🛡️ SENTINEL OMEGA", fg="white", bg=HEX_FONDO, font=("Impact", 55)).pack(pady=(40, 5))
        tk.Label(self.container, text="CUIDANDO TU CAMINO Y TU SONRISA", fg="#00A8E8", bg=HEX_FONDO, font=("Comic Sans MS", 14, "italic")).pack()
        tk.Label(self.container, text="Tu vida es valiosa y estamos aquí para protegerte.", fg="#666", bg=HEX_FONDO, font=("Arial", 10)).pack(pady=5)

        # Sección de Botones de Pánico
        btn_f = tk.Frame(self.container, bg=HEX_FONDO)
        btn_f.pack(pady=30)
        
        tk.Button(btn_f, text="☢ CÓDIGO ROJO", bg="#8B0000", fg="white", font=("Arial", 14, "bold"), 
                  width=22, height=2, relief="flat", command=self.lanzar_selector_rojo).grid(row=0, column=0, padx=10)
        
        tk.Button(btn_f, text="🆘 AUXILIO S.O.S", bg="#B8860B", fg="black", font=("Arial", 14, "bold"), 
                  width=22, height=2, relief="flat", command=self.lanzar_sos).grid(row=0, column=1, padx=10)

        # Entrada de Texto con Estilo Terminal
        tk.Label(self.container, text="¿QUÉ ESTÁ PASANDO? CUÉNTANOS CON CONFIANZA:", fg="#AAA", bg=HEX_FONDO, font=("Arial", 9, "bold")).pack()
        self.txt_input = scrolledtext.ScrolledText(self.container, width=70, height=10, bg="#111", fg=HEX_TEXTO_IA, 
                                                  font=("Consolas", 13), insertbackground="white", bd=0)
        self.txt_input.pack(pady=10)

        # Botones de Acción Social
        tk.Button(self.container, text="🙋 QUIERO CONTAR ALGO QUE VI (MODO TESTIGO)", bg="#1A3A5A", fg="white", 
                  width=50, height=2, relief="flat", command=self.modo_testigo).pack(pady=5)
                  
        tk.Button(self.container, text="ENVIAR A MIS PROTECTORES", bg="white", fg="black", font=("Arial", 12, "bold"), 
                  width=50, height=2, relief="flat", command=self.analizar_y_enviar).pack(pady=25)

        # Botón de Sistema casi invisible para el usuario común
        tk.Button(self.container, text="[ ACCESO SISTEMA ]", bg=HEX_FONDO, fg="#111", bd=0, 
                  activebackground=HEX_FONDO, command=self.admin_auth).pack(side="bottom", pady=15)

    def modo_testigo(self):
        """Prepara el campo de texto para un reporte de terceros."""
        self.txt_input.delete("1.0", tk.END)
        self.txt_input.insert("1.0", "HOLA, QUIERO REPORTAR QUE: ")
        self.txt_input.focus_set()

    # --- MÓDULO S.O.S (SEGURIDAD Y CALMA PSICOLÓGICA) ---
    def lanzar_sos(self):
        """Abre una ventana dedicada a la ubicación rápida del usuario en peligro."""
        v = tk.Toplevel(self.root)
        v.title("S.O.S - AYUDA EN CAMINO")
        v.geometry("400x600")
        v.configure(bg="#1A1A1A")
        v.grab_set() # Bloquea la interacción con la ventana principal

        tk.Label(v, text="¡TRANQUILO(A)!", fg="#00FF00", bg="#1A1A1A", font=("Arial", 18, "bold")).pack(pady=(20,5))
        tk.Label(v, text="Tu vida es lo más importante para nosotros.\nDinos dónde estás, la ayuda ya viene en camino.", 
                 fg="white", bg="#1A1A1A", font=("Arial", 10), justify="center").pack(pady=5)
        
        # Botones de Ubicaciones Frecuentes en la Sede
        puntos = ["BIBLIOTECA", "CASINO", "SALA DE COMPUTACIÓN", "BAÑOS", "PATIO CENTRAL", "ESTACIONAMIENTO"]
        for p in puntos:
            tk.Button(v, text=p, bg="#333", fg="white", width=30, pady=8, relief="flat",
                      command=lambda loc=p: [v.destroy(), self.finalizar_sos(loc)]).pack(pady=4)
        
        tk.Label(v, text="¿Estás en otro lugar? Escríbelo aquí abajo:", fg="#888", bg="#1A1A1A").pack(pady=(15,0))
        ent = tk.Entry(v, width=35, font=("Arial", 12))
        ent.pack(pady=10)
        
        # REGLA DE ORO: Capturamos el texto del Entry antes de destruir la ventana Toplevel.
        tk.Button(v, text="ENVIAR MI UBICACIÓN", bg=HEX_NARANJA, font=("Arial", 10, "bold"),
                  command=lambda: self.validar_sos_custom(ent, v)).pack(pady=15)

    def validar_sos_custom(self, entry_widget, ventana):
        """Extrae la información de ubicación y procede al cierre seguro."""
        lugar_texto = entry_widget.get()
        ventana.destroy()
        self.finalizar_sos(lugar_texto)

    def finalizar_sos(self, lugar):
        """Finaliza el proceso de SOS registrando el evento y dando calma."""
        if not lugar: lugar = "Ubicación por confirmar (Usuario en Shock)"
        folio = f"SOS-{random.randint(100, 999)}"
        self.db.insertar("SOLICITUD URGENTE DE AYUDA S.O.S", "CRÍTICO", 500, folio, "VÍCTIMA", f"LUGAR: {lugar}")
        messagebox.showwarning("S.O.S RECIBIDO", "¡YA TE ESCUCHAMOS!\n\nNo tengas miedo, busca un lugar seguro y quédate ahí. Tus protectores están llegando.")

    # --- MÓDULO CÓDIGO ROJO (BLOQUEO DE EMERGENCIA) ---
    def lanzar_selector_rojo(self):
        """Selector rápido para el tipo de amenaza mayor."""
        m = tk.Toplevel(self.root)
        m.title("CÓDIGO ROJO")
        m.geometry("400x320")
        m.configure(bg="#200000")
        m.grab_set()
        
        opciones = [("🔫 TIROTEO / ARMAS DE FUEGO", "TIROTEO"), 
                    ("🔥 INCENDIO / FUEGO ACTIVO", "INCENDIO"), 
                    ("💣 AMENAZA DE BOMBA", "BOMBA")]
        for txt, tipo in opciones:
            tk.Button(m, text=txt, bg="#600000", fg="white", width=35, pady=12, relief="flat",
                      command=lambda t=tipo: [m.destroy(), self.ejecutar_bloqueo_rojo(f"ALERTA MANUAL: {t}")]).pack(pady=10)

    def ejecutar_bloqueo_rojo(self, motivo):
        """Activa el protocolo de pantalla completa y alerta sonora visual."""
        self.db.insertar(f"ALERTA CÓDIGO ROJO: {motivo}", "CÓDIGO ROJO", 1000, "RED-ALERT", "SISTEMA", obtener_geolocalizacion_real())
        
        self.bloqueo = tk.Toplevel(self.root)
        self.bloqueo.attributes("-fullscreen", True)
        self.bloqueo.attributes("-topmost", True) # Asegura que la alerta no se oculte
        self.bloqueo.configure(bg=HEX_ROJO)
        
        tk.Label(self.bloqueo, text="🚨 CÓDIGO ROJO 🚨", fg="white", bg=HEX_ROJO, font=("Arial", 85, "bold")).pack(expand=True)
        tk.Label(self.bloqueo, text="MANTÉNGASE EN CALMA Y SILENCIO\nTU VIDA ES LO MÁS VALIOSO PARA NOSOTROS", 
                 fg="white", bg=HEX_ROJO, font=("Arial", 35), justify="center").pack(expand=True)
        
        tk.Button(self.bloqueo, text="DESACTIVAR ALERTA (SÓLO PERSONAL AUTORIZADO)", font=("Arial", 18, "bold"), 
                  command=self.crear_dialogo_pin).pack(pady=60)

    def crear_dialogo_pin(self):
        """Ventana de PIN con prioridad visual absoluta para el desbloqueo."""
        p_win = tk.Toplevel(self.bloqueo)
        p_win.title("ACCESO RESTRINGIDO")
        p_win.geometry("350x220")
        p_win.attributes("-topmost", True)
        p_win.configure(bg="#1A1A1A")
        p_win.grab_set()
        
        tk.Label(p_win, text="INGRESE PIN DE DESBLOQUEO:", fg="white", bg="#1A1A1A", font=("Arial", 11, "bold")).pack(pady=20)
        e = tk.Entry(p_win, show="*", font=("Arial", 30), justify="center", width=10)
        e.pack(pady=10)
        e.focus_set()
        
        tk.Button(p_win, text="CONFIRMAR DESBLOQUEO", bg="#2E86C1", fg="white", font=("Arial", 10, "bold"),
                  command=lambda: self.validar_pin_rojo(e.get(), p_win)).pack(pady=20)

    def validar_pin_rojo(self, val, win):
        """Valida el pin y libera el bloqueo del sistema."""
        if val == PIN_DESBLOQUEO:
            win.destroy()
            self.bloqueo.destroy()
        else:
            messagebox.showerror("ERROR DE SEGURIDAD", "PIN INCORRECTO - EL BLOQUEO PERSISTE", parent=win)

    def analizar_y_enviar(self):
        """Analiza el reporte escrito, decide el nivel de riesgo y lo procesa."""
        texto = self.txt_input.get("1.0", tk.END).strip()
        if len(texto) < 5: return

        riesgo, pts = MotorAnalisis.clasificar(texto)
        
        if riesgo == "CÓDIGO ROJO":
            self.ejecutar_bloqueo_rojo(texto[:50])
        else:
            folio = f"SO-{random.randint(10000, 99999)}"
            self.db.insertar(texto, riesgo, pts, folio, "USUARIO", obtener_geolocalizacion_real())
            messagebox.showinfo("MENSAJE RECIBIDO", "¡Gracias por avisarnos! Eres muy valiente.\nYa estamos trabajando para que todo esté bien.")
            self.pantalla_inicio()

    # --- PANEL DE ADMINISTRACIÓN (CENTRO DE CONTROL) ---
    def admin_auth(self):
        """Autenticación para acceder a los datos sensibles de la sede."""
        # Forzamos que el diálogo de clave aparezca sobre la raíz para no perder el foco.
        clave = simpledialog.askstring("CONTROL DE MANDO", "Ingrese Clave Maestra de Acceso:", show="*", parent=self.root)
        if clave == ADMIN_CLAVE:
            self.pantalla_admin()
        elif clave is not None:
            messagebox.showerror("ACCESO DENEGADO", "La clave ingresada no es válida.")

    def pantalla_admin(self):
        """Vista exclusiva para el personal de seguridad con métricas e historial."""
        for w in self.container.winfo_children(): w.destroy()
        
        # Estilización de la Tabla de Incidentes
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="#111", foreground="white", fieldbackground="#111", rowheight=32)
        
        self.tree = ttk.Treeview(self.container, columns=("ID", "Folio", "Nivel", "Estado", "Fecha"), show="headings", height=10)
        for col in ("ID", "Folio", "Nivel", "Estado", "Fecha"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="x", padx=30, pady=20)

        # Configuración de colores visuales por fila según el riesgo detectado.
        self.tree.tag_configure('CÓDIGO ROJO', background=HEX_ROJO, foreground='white')
        self.tree.tag_configure('CRÍTICO', background=HEX_MORADO, foreground='white')
        self.tree.tag_configure('ALTO', background=HEX_NARANJA, foreground='white')
        self.tree.tag_configure('MODERADO', background=HEX_AZUL, foreground='white')
        self.tree.tag_configure('BAJO', background=HEX_CELESTE, foreground='black')

        # Contenedor para el Gráfico Estadístico de la jornada.
        self.graph_f = tk.Frame(self.container, bg=HEX_FONDO, height=350)
        self.graph_f.pack(fill="both", expand=True)

        # Panel de Acciones Administrativas
        ctrls = tk.Frame(self.container, bg=HEX_FONDO)
        ctrls.pack(pady=20)
        
        tk.Button(ctrls, text="CERRAR CASO", bg="#1B4721", fg="white", width=20, command=self.admin_finalizar).grid(row=0, column=0, padx=5)
        tk.Button(ctrls, text="VER ACTA PDF", bg="#2E86C1", fg="white", width=20, command=self.admin_export_pdf).grid(row=0, column=1, padx=5)
        tk.Button(ctrls, text="HISTORIAL EXCEL", bg="#1D6F42", fg="white", width=20, command=self.admin_export_excel).grid(row=0, column=2, padx=5)
        
        # Función de salida para regresar al modo usuario de forma segura.
        tk.Button(self.container, text="CERRAR SESIÓN Y VOLVER AL MODO PROTECCIÓN", bg="#333", fg="white", 
                  relief="flat", command=self.pantalla_inicio).pack(pady=10)
        
        self.refrescar_datos()

    def refrescar_datos(self):
        """Actualiza la tabla y el gráfico con los datos más recientes de la DB."""
        for i in self.tree.get_children(): self.tree.delete(i)
        self.db.cursor.execute("SELECT id, folio, nivel_riesgo, estado, fecha FROM reportes ORDER BY id DESC")
        for r in self.db.cursor.fetchall():
            self.tree.insert("", tk.END, values=r, tags=(r[2],))
        self.actualizar_grafico()

    def actualizar_grafico(self):
        """Genera un gráfico circular con la distribución actual de incidentes."""
        for w in self.graph_f.winfo_children(): w.destroy()
        df = pd.read_sql_query("SELECT nivel_riesgo FROM reportes", self.db.conn)
        if df.empty: return
        
        fig, ax = plt.subplots(figsize=(5, 3.5), dpi=85)
        fig.patch.set_facecolor(HEX_FONDO)
        cmap = {'CÓDIGO ROJO': HEX_ROJO, 'CRÍTICO': HEX_MORADO, 'ALTO': HEX_NARANJA, 'MODERADO': HEX_AZUL, 'BAJO': HEX_CELESTE}
        
        counts = df['nivel_riesgo'].value_counts()
        counts.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=[cmap.get(x, '#555') for x in counts.index], textprops={'color':"w"})
        ax.set_ylabel('')
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_f)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def admin_finalizar(self):
        """Cierra el ciclo de vida de un reporte, marcándolo como resuelto."""
        sel = self.tree.selection()
        if sel:
            rid = self.tree.item(sel[0])['values'][0]
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.cursor.execute("UPDATE reportes SET estado='FINALIZADO', fecha_resolucion=? WHERE id=?", (ahora, rid))
            self.db.conn.commit()
            self.refrescar_datos()

    def admin_export_pdf(self):
        """Extrae el caso seleccionado y lo convierte en un documento PDF formal."""
        sel = self.tree.selection()
        if not sel: return
        rid = self.tree.item(sel[0])['values'][0]
        self.db.cursor.execute("SELECT * FROM reportes WHERE id=?", (rid,))
        d = self.db.cursor.fetchone()
        
        pdf = GeneradorActa()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"FOLIO DE INCIDENTE: {d[5]} | CLASIFICACIÓN: {d[3]}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 10, f"FECHA REGISTRO: {d[1]}\nUBICACIÓN: {d[7]}\nROL DEL INFORMANTE: {d[8]}\n\nDETALLE DE LA NOVEDAD:\n{d[2]}", border=1)
        
        ruta = f"REPORTES_PDF/ACTA_{d[5]}.pdf"
        pdf.output(ruta)
        # Abrimos la carpeta para que el operador vea el archivo generado.
        webbrowser.open(os.path.abspath("REPORTES_PDF"))

    def admin_export_excel(self):
        """Exporta la base de datos completa a Excel para auditorías externas."""
        df = pd.read_sql_query("SELECT * FROM reportes", self.db.conn)
        df.to_excel("EXPORTS/HISTORIAL_COMPLETO_SENTINEL_OMEGA.xlsx", index=False)
        webbrowser.open(os.path.abspath("EXPORTS"))

# =============================================================================
# INICIO DE LA APLICACIÓN (ENTRY POINT)
# =============================================================================
if __name__ == "__main__":
    # Creamos la raíz de Tkinter y lanzamos nuestra obra maestra.
    root = tk.Tk()
    app = SentinelOmegaApp(root)
    root.mainloop()
# FIN DEL ARCHIVO - SENTINEL OMEGA v0.1.1 MASTER