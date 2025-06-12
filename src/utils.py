import os
import sys
import json
import tkinter as tk

CONFIG_FILE = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), 'config.json')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, "assets", relative_path)

TRANSLATIONS = {
    "es": {
        "domain_input": "Introducir dominios",
        "analyze_domains": "Analizar Dominios",
        "copy_all": "Copiar Todos",
        "copy_all_confirm": "Se han copiado todos los dominios analizados excepto los rojos al portapapeles.",
        "copy_color": "Los dominios de color {color} han sido copiados al portapapeles.",
        "no_domains_to_copy": "No hay dominios analizados para copiar.",
        "green": "verde",
        "yellow": "amarillo",
        "orange": "naranja",
        "red": "rojo",
        "configure_api_keys": "Por favor, configure al menos una clave API en el menú de Configuración.",
        "configure_cx_key": "Por favor, configure la clave CX en el menú de Configuración.",
        "configure_both_keys": "Por favor, configure al menos una clave API y la clave CX en el menú de Configuración.",
        "enter_domains": "Por favor, ingresa al menos un dominio antes de analizar.",
        "api_limit_reached": "Todas las claves de API han alcanzado el límite diario de consultas.",
        "api_keys_used": "Claves API utilizadas: {count}",
        "domain_results": "Dominio\t\tTotal de Resultados",
        "divider": "=" * 50,
        "config_menu_label": "Configuración",
        "change_language": "Change Language",
        "api_keys": "Claves API",
        "add_api_key_button": "Agregar clave API",
        "delete_api_key_button": "Eliminar Seleccionada",
        "verify_api_keys_button": "Verificar claves API",
        "status": "Estado",
        "cx": "CX",
        "add_cx_button": "Agregar clave CX",
        "paste_api_key_here": "Pega la clave API aquí y haz clic en Agregar",
        "urls_indexed": "URLs indexadas",
        "export_csv": "Exportar CSV",
        "csv_export_success": "CSV exportado exitosamente.",
        "analyzing_text": "Analizando",
        "paste": "Pegar",
        "copy": "Copiar",
        "invalid_cx_error": "La clave CX es inválida. Por favor, configura una clave CX válida.",
        "donations_view_qr": "Ver codigo QR",
        "api_guide": (
            "Pasos para obtener la clave API de Google Custom Search:\n\n"
            "1. Crea un nuevo proyecto:\n"
            "   - Ve a la Consola de Google Cloud.\n"
            "   - Crea un nuevo proyecto.\n\n"
            "2. Habilita la API de Google Custom Search:\n"
            "   - En el menú \"APIs y servicios\", selecciona \"Habilitar APIs y servicios\".\n"
            "   - Busca \"Custom Search API\" y haz clic en \"Habilitar\".\n\n"
            "3. Obtén tu clave API:\n"
            "   - Ve a \"Credenciales\" en el menú lateral.\n"
            "   - Haz clic en \"Crear credenciales\" y selecciona \"Clave de API\".\n"
            "   - Copia la clave generada y pégala aquí.\n\n"
            "Límites de uso diario:\n"
            "Cada clave API permite consultar hasta 100 dominios al día de forma gratuita. Puedes agregar varias claves API creando nuevos proyectos. "
            "Si necesitas realizar muchas consultas diarias, puedes habilitar la facturación en Google Cloud para aumentar el límite hasta 10,000 "
            "búsquedas, pagando $5 por cada 1,000 búsquedas adicionales."
        ),
        "cx_guide": (
            "Pasos para obtener la clave CX:\n\n"
            "   - Ve a Google Custom Search Engine.\n"
            "   - Crea un nuevo motor de búsqueda.\n"
            "   - Configura el motor para buscar en toda la web.\n"
            "   - Obtén el ID del motor de búsqueda (cx) y pégalo aquí."
        ),
        "cuota_api_superada": "Cuota API superada",
        "clear_results": "Borrar resultados",
        "filter_domains": "Filtrar Dominios",
        "tooltip_filter": "Filtra cualquier texto y deja solo los dominios, eliminando duplicados.",
        "tooltip_search": "Filtra y analiza los dominios para obtener las URLs indexadas.",
        "tooltip_copy_all": "Copia todos los dominios analizados excepto los que están en rojo.",
        "tooltip_copy_green": "Copia los dominios marcados en verde.",
        "tooltip_copy_yellow": "Copia los dominios marcados en amarillo.",
        "tooltip_copy_orange": "Copia los dominios marcados en naranja.",
        "tooltip_export_csv": "Exporta los resultados a un archivo CSV.",
        "tooltip_clear_results": "Borra los resultados mostrados.",
        "help_menu_label": "Ayuda",
        "help_documentation": "Documentación",
        "help_about": "Acerca de",
        "help_donations": "Donaciones",
        "help_documentation_text": (
            "GIndexChecker es una herramienta para analizar la indexación de dominios y URLs en Google de forma masiva.\n\n"
            "¿Cómo usar?\n\n"
            "    • Configura tus claves API y CX en el menú de Configuración.\n"            
            "    • Pega en el cuadro principal un listado que incluya dominios (puede contener otros textos).\n"
            "    • Haz clic en “Analizar Dominios” para obtener los resultados.\n"
            "    • Puedes exportar los resultados a CSV o copiarlos al portapapeles.\n"
            "    • Haz clic en un dominio para abrir una búsqueda site: en el navegador y comprobar la indexación manualmente.\n\n"
            "Notas:\n\n"
            "    • Los resultados dependen de la API de Google y pueden no ser exactos en todos los casos.\n\n"
            "Más información y soporte: [Repositorio en GitHub](https://github.com/TaoPaiAI/gindexchecker)"
        ),
        "help_about_text": (
            "GIndexChecker\n"
            "Versión: 1.0\n"
            "Autor: TaoPaiAI\n"
            "Repositorio: [Repositorio en GitHub](https://github.com/TaoPaiAI/gindexchecker)\n"
            "Licencia: MIT [Ver detalles de la licencia](https://github.com/TaoPaiAI/gindexchecker/blob/main/LICENSE)"
        ),
        "help_donations_text": (
            "¡Gracias por tu interés en apoyar este proyecto!\n\n"
            "Si GIndexChecker te resulta útil y quieres contribuir a su desarrollo y mantenimiento, puedes hacer una donación voluntaria.\n"
            "Tu apoyo ayuda a que siga mejorando y siendo gratuito para todos.\n\n"
            "    Bitcoin: bc1qs4n97g4k65rmqymzw3q6syg75m3z3yun9kfk39"
        )
    },
    "en": {
        "domain_input": "Enter domains",
        "analyze_domains": "Analyze Domains",
        "copy_all": "Copy All",
        "copy_all_confirm": "All analyzed domains except those marked in red have been copied to the clipboard.",
        "copy_color": "Domains of color {color} have been copied to the clipboard.",
        "no_domains_to_copy": "There are no analyzed domains to copy.",
        "green": "Green",
        "yellow": "Yellow",
        "orange": "Orange",
        "red": "red",
        "configure_api_keys": "Please configure at least one API key in the Settings menu.",
        "configure_cx_key": "Please configure the CX key in the Settings menu.",
        "configure_both_keys": "Please configure at least one API key and the CX key in the Settings menu.",
        "enter_domains": "Please enter at least one domain before analyzing.",
        "api_limit_reached": "All API keys have reached their daily limit.",
        "api_keys_used": "API keys used: {count}",
        "domain_results": "Domain\t\tTotal Results",
        "divider": "=" * 50,
        "config_menu_label": "Settings",
        "change_language": "Cambiar Idioma",
        "api_keys": "API Keys",
        "add_api_key_button": "Add API Key",
        "delete_api_key_button": "Delete Selected",
        "verify_api_keys_button": "Verify API Keys",
        "status": "Status",
        "cx": "CX",
        "add_cx_button": "Add CX Key",
        "paste_api_key_here": "Paste the API key here and click Add",
        "urls_indexed": "indexed URLs",
        "export_csv": "Export CSV",
        "csv_export_success": "CSV exported successfully.",
        "analyzing_text": "Analyzing",
        "paste": "Paste",
        "copy": "Copy",
        "invalid_cx_error": "The CX key is invalid. Please configure a valid CX key.",
        "donations_view_qr": "View QR Code",
        "api_guide": (
            "Steps to obtain the Google Custom Search API key:\n\n"
            "1. Create a new project:\n"
            "   - Go to the Google Cloud Console.\n"
            "   - Create a new project.\n\n"
            "2. Enable the Google Custom Search API:\n"
            "   - In the \"APIs & Services\" menu, select \"Enable APIs and Services\".\n"
            "   - Search for \"Custom Search API\" and click \"Enable\".\n\n"
            "3. Get your API key:\n"
            "   - Go to \"Credentials\" in the sidebar.\n"
            "   - Click \"Create credentials\" and select \"API key\".\n"
            "   - Copy the generated key and paste it here.\n\n"
            "Daily usage limits:\n"
            "Each API key allows querying up to 100 domains per day for free. You can add multiple API keys by creating new projects. "
            "If you need to perform many daily queries, you can enable billing on Google Cloud to increase the limit up to 10,000 "
            "searches, paying $5 for every 1,000 additional searches."
        ),
        "cx_guide": (
            "Steps to obtain the CX key:\n\n"
            "   - Go to Google Custom Search Engine.\n"
            "   - Create a new search engine.\n"
            "   - Configure the search engine to search the entire web.\n"
            "   - Get the search engine ID (cx) and paste it here."
        ),
        "cuota_api_superada": "API quota exceeded",
        "clear_results": "Clear Results",
        "filter_domains": "Filter Domains",
        "tooltip_filter": "Filters any text, leaving only domains and removing duplicates.",
        "tooltip_search": "Filters and analyzes domains to obtain indexed URLs.",
        "tooltip_copy_all": "Copies all analyzed domains except those marked in red.",
        "tooltip_copy_green": "Copies domains marked in green.",
        "tooltip_copy_yellow": "Copies domains marked in yellow.",
        "tooltip_copy_orange": "Copies domains marked in orange.",
        "tooltip_export_csv": "Exports the results to a CSV file.",
        "tooltip_clear_results": "Clears the displayed results.",
        "help_menu_label": "Help",
        "help_documentation": "Documentation",
        "help_about": "About",
        "help_donations": "Donations",
        "help_documentation_text": (
            "GIndexChecker is a tool for analyzing the indexation of domains and URLs in Google at scale.\n\n"
            "How to use?\n\n"
            "    • Configure your API and CX keys in the settings menu.\n"           
            "    • Paste into the main box a list that includes domains (it can contain other text).\n"
            "    • Click “Analyze Domains” to get the results.\n"
            "    • You can export results to CSV or copy them to the clipboard.\n"
            "    • Click a domain to open a site: search in the browser and check indexing manually.\n\n"
            "Notes:\n\n"
            "    • Results depend on the Google API and may not be exact in all cases.\n\n"
            "More information and support: [GitHub repository](https://github.com/TaoPaiAI/gindexchecker)"
        ),
        "help_about_text": (
            "GIndexChecker\n"
            "Version: 1.0\n"
            "Author: TaoPaiAI\n"
            "Repository: [GitHub repository](https://github.com/TaoPaiAI/gindexchecker)\n"
            "License: MIT [See license details](https://github.com/TaoPaiAI/gindexchecker/blob/main/LICENSE)"
        ),
        "help_donations_text": (
            "Thank you for your interest in supporting this project!\n\n"
            "If GIndexChecker is useful to you and you want to contribute to its development and maintenance, you can make a voluntary donation.\n"
            "Your support helps it keep improving and remain free for everyone.\n\n"
            "    Bitcoin: bc1qs4n97g4k65rmqymzw3q6syg75m3z3yun9kfk39"
        )
    }
}

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        return {'API_KEYS': [], 'CX': '', 'language': "es"}

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

def set_app_icon(root):
    if sys.platform.startswith("win"):
        root.iconbitmap(resource_path("gindexchecker2.ico"))
    else:
        icon_path = resource_path("gindexchecker2.png")
        if os.path.exists(icon_path):
            icon_img = tk.PhotoImage(file=icon_path)
            root.wm_iconphoto(True, icon_img)