import os
import sys
import time
import re
from datetime import datetime
from pypdf import PdfReader
import ollama  
from playwright.sync_api import sync_playwright

# =====================================================================
# ⚙️ CONFIGURACIÓN DE TU ESTRATEGIA (Modelo base de texto rápido)
# =====================================================================
MODELO_ACTIVO = 'llama3.2'
# =====================================================================

def leer_cv(ruta_pdf):
    if not os.path.exists(ruta_pdf):
        print(f"[!] Error: No se encuentra el archivo '{ruta_pdf}' en esta carpeta.")
        sys.exit(1)
    lector = PdfReader(ruta_pdf)
    texto_cv = ""
    for pagina in lector.pages:
        texto_cv += pagina.extract_text()
    return texto_cv

def capturar_oferta_directa():
    try:
        with sync_playwright() as p:
            print("🔗 Conectando con la ventana especial de Chrome...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=5000)
            
            if not browser.contexts:
                print("[!] Error: No se detecta ningún perfil activo en tu Chrome especial.")
                sys.exit(1)
                
            contexto_activo = browser.contexts[0]
            pages = contexto_activo.pages
            
            if not pages:
                print("[!] Error: No hay ninguna pestaña abierta.")
                sys.exit(1)
            
            page = None
            for p_actual in pages:
                url_actual = p_actual.url.lower()
                if "linkedin" not in url_actual and "http" in url_actual:
                    page = p_actual
                    break
            
            if not page:
                page = pages[-1]
            
            print(f"📖 Leyendo la pantalla del empleador: {page.title()}")
            print(f"🔗 URL Detectada: {page.url}")
            
            print("⏳ Sincronizando elementos de la página...")
            page.wait_for_timeout(2000)
            
            print("✨ Extrayendo texto crudo de la oferta...")
            texto_oferta = page.evaluate("() => document.body.innerText")
            
            return texto_oferta
    except Exception as e:
        print(f"\n[!] ERROR CRÍTICO DE CONEXIÓN CON TU NAVEGADOR: {e}\n")
        sys.exit(1)

def obtener_palabras_clave_ia(oferta, modelo):
    try:
        cliente_ollama = ollama.Client(host='http://127.0.0.1:11434')
        prompt_slug = f"""
        Lee este texto de empleo y extrae únicamente el título del puesto resumido en 2 o 3 palabras clave.
        Devuelve estrictamente las palabras en minúsculas, sin espacios, separadas por guiones bajos y sin ningún otro texto.
        
        Ejemplo: engineering_manager_product
        
        Texto:
        {oferta[:500]}
        """
        res = cliente_ollama.generate(model=modelo, prompt=prompt_slug)['response']
        slug = res.strip().replace(" ", "_").lower()
        slug = re.sub(r'[^a-z0-9__]', '', slug)
        return slug if slug else "puesto_trabajo"
    except:
        return "puesto_trabajo"

def analizar_con_ia(cv, oferta, modelo):
    print(f"\n🤖 PASO 1: Evaluando compatibilidad inicial en Ollama ({modelo})...")
    
    tiempo_inicio = time.time()
    
    try:
        cliente_ollama = ollama.Client(host='http://127.0.0.1:11434')
        
        # PROMPT OPTIMIZADO: Ya no le pedimos la carta de presentación aquí para ahorrar tiempo
        prompt_compatibilidad = f"""
        Compara los datos de mi CV con la oferta de empleo obtenida directamente de la web del empleador.
        Evalúa si mi perfil es apto.
        
        Texto de la Oferta:
        {oferta}
        
        Mi CV:
        {cv}
        
        Devuelve estrictamente este formato en ESPAÑOL:
        ### COMPATIBILIDAD
        [Nota del 1 al 10 en formato número/10, ejemplo: 9/10 o 7/10, seguido del motivo clave de la calificación en 2 líneas]
        
        ### REQUISITOS CLAVE DETECTADOS
        [Lista de los 3 requisitos más importantes que se piden para el puesto]
        """
        
        res_inicial = cliente_ollama.generate(model=modelo, prompt=prompt_compatibilidad)['response']
        
        # Extraer la nota numérica del reporte inicial
        coincidencia_nota = re.search(r'(\d+)/10', res_inicial)
        nota = 0
        if coincidencia_nota:
            nota = int(coincidencia_nota.group(1))
        
        print("\n" + "="*50 + "\n 📊 RESULTADO DE COMPATIBILIDAD\n" + "="*50)
        print(res_inicial)
        
        # EVALUACIÓN DE FILTRO INTELIGENTE
        if nota >= 8:
            print(f"\n🚀 ¡Excelente compatibilidad ({nota}/10)! PASO 2: Generando carta de presentación...")
            
            prompt_carta = f"""
            Redacta una propuesta de carta de presentación corta de un máximo de 2 párrafos en ESPAÑOL para postularme a este puesto. Usa los datos de mi CV para que sea coherente.
            
            Puesto (Oferta): {oferta[:600]}
            Mi CV: {cv}
            """
            
            res_carta = cliente_ollama.generate(model=modelo, prompt=prompt_carta)['response']
            
            print("\n" + "="*50 + "\n 📝 CARTA DE PRESENTACIÓN COHERENTE GENERADA\n" + "="*50)
            print(res_carta)
            
            # Crear carpeta con la fecha DDMMAAAA
            fecha_hoy = datetime.now().strftime("%d%m%Y")
            if not os.path.exists(fecha_hoy):
                os.makedirs(fecha_hoy)
            
            # Obtener palabras clave para nombrar archivos
            palabras_clave = obtener_palabras_clave_ia(oferta, modelo)
            
            nombre_oferta = os.path.join(fecha_hoy, f"{palabras_clave}_ofert.txt")
            nombre_carta = os.path.join(fecha_hoy, f"{palabras_clave}_motivation_letter.txt")
            
            # Guardar archivos en la carpeta
            with open(nombre_oferta, "w", encoding="utf-8") as f:
                f.write(oferta)
            
            with open(nombre_carta, "w", encoding="utf-8") as f:
                informe_completo = f"{res_inicial}\n\n### CARTA DE PRESENTACIÓN\n{res_carta}"
                f.write(informe_completo)
                
            print(f"\n💾 Archivos organizados con éxito en la carpeta '{fecha_hoy}':")
            print(f"   - {nombre_oferta}")
            print(f"   - {nombre_carta}")
        else:
            print(f"\n📉 Nota: {nota}/10. Al ser menor de 8/10, se bloquea la redacción de la carta y el guardado de archivos.")

        tiempo_fin = time.time()
        segundos_totales = round(tiempo_fin - tiempo_inicio, 2)
        print(f"\n⏱️ TIEMPO DE PROCESAMIENTO: El i5 tardó exactamente {segundos_totales} segundos.")
        
    except Exception as e:
        print(f"\n[!] ERROR AL GENERAR EL ANÁLISIS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    archivo_cv = "mi_cv.pdf"
    texto_mi_cv = leer_cv(archivo_cv) 
    texto_de_la_oferta = capturar_oferta_directa()
    analizar_con_ia(texto_mi_cv, texto_de_la_oferta, MODELO_ACTIVO)
