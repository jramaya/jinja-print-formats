import os
from flask import Flask, render_template, make_response

app = Flask(__name__)

# Directorio base de las plantillas de reportes
REPORTS_DIR = os.path.join('templates', 'reports')

@app.route('/')
def index():
    """
    Muestra una lista de todos los reportes disponibles.
    """
    try:
        # Obtiene los nombres de las carpetas de los reportes
        report_names = [name for name in os.listdir(REPORTS_DIR)
                        if os.path.isdir(os.path.join(REPORTS_DIR, name))]
    except FileNotFoundError:
        # Si la carpeta de reportes no existe, muestra una lista vacía
        report_names = []
        
    return render_template('index.html', reports=report_names)

@app.route('/report/<report_name>')
def generate_report(report_name):
    """
    Renderiza un reporte buscando todas las páginas de contenido
    en la carpeta correspondiente.
    """
    report_folder = os.path.join(REPORTS_DIR, report_name)
    
    if not os.path.isdir(report_folder):
        return "Reporte no encontrado", 404

    # Carga el contenido de cada página del reporte
    pages_content = []
    page_files = sorted(os.listdir(report_folder)) # Ordena para asegurar page1, page2, etc.
    
    for page_file in page_files:
        if page_file.endswith('.html'):
            # La ruta para render_template debe ser relativa a la carpeta 'templates'
            # y usar barras diagonales (/) para que Jinja la encuentre, sin importar el S.O.
            template_path = f"reports/{report_name}/{page_file}"
            # Renderizamos cada página por si tuviera lógica Jinja dentro
            pages_content.append(render_template(template_path))
            
    return render_template('base.html', pages=pages_content)

@app.route('/static/css/style.css')
def serve_css():
    """
    Sirve la hoja de estilos, renderizándola como una plantilla Jinja.
    Esto te permite usar variables en tu CSS en el futuro.
    """
    css_template = render_template('css/style.css.j2')
    response = make_response(css_template)
    response.headers['Content-Type'] = 'text/css'
    return response

if __name__ == '__main__':
    # Para acceder desde la red local, usa host='0.0.0.0'
    app.run(debug=True, port=5001)