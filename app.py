import os
import json
import re
from flask import Flask, render_template, render_template_string, abort, make_response, url_for

# Nuevas importaciones para el resaltado de sintaxis
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

# Nuevas importaciones para incrustar imágenes
import base64
import mimetypes

app = Flask(__name__)

REPORTS_PATH = os.path.join('templates', 'documents')
TEMPLATES_PATH = 'templates'

# --- MISTUNE & PYGMENTS SETUP ---
# Crea un renderizador personalizado que usa Pygments para los bloques de código.
class HighlightRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        if info:
            lexer = get_lexer_by_name(info, stripall=True)
            formatter = HtmlFormatter(style='colorful', cssclass='highlight')
            return highlight(code, lexer, formatter)
        return '<pre><code>' + mistune.escape(code) + '</code></pre>'

# Instancia el procesador de Markdown con nuestro renderizador personalizado.
markdown_parser = mistune.create_markdown(renderer=HighlightRenderer())

def _embed_images_as_base64(html_content):
    """
    Busca etiquetas de imagen con una estructura url_for específica y reemplaza el src
    con un URI de datos base64 incrustado.
    """
    # Este regex encuentra el atributo src completo para su reemplazo.
    # Captura el nombre de archivo de url_for('static', filename=...).
    pattern = re.compile(r'(src\s*=\s*["\']{{\s*url_for\(\s*\'static\',\s*filename=[\'"](.+?)[\'"]\s*\)\s*}}["\'])')

    def replacer(match):
        full_src_attribute = match.group(1)
        filename = match.group(2)
        # Construye la ruta, asegurando que sea independiente del sistema operativo
        image_path = os.path.join('static', *filename.split('/'))

        # Si la imagen no existe, devuelve el atributo original para no romper la vista.
        if not os.path.exists(image_path):
            print(f"Advertencia: No se encontró la imagen en la ruta: {image_path}")
            return full_src_attribute

        try:
            mime_type, _ = mimetypes.guess_type(image_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'

            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # Devuelve el nuevo atributo src con el URI base64
            return f'src="data:{mime_type};base64,{encoded_string}"'
        except Exception as e:
            # En caso de cualquier otro error, devuelve el original para no romper la vista
            print(f"No se pudo incrustar la imagen {filename}: {e}")
            return full_src_attribute

    return pattern.sub(replacer, html_content)

@app.route('/')
def index():
    """Lists all available documents."""
    try:
        documents = [d for d in os.listdir(REPORTS_PATH) if os.path.isdir(os.path.join(REPORTS_PATH, d))]
        return render_template('index.html', documents=documents)
    except FileNotFoundError:
        return "The 'templates/documents' directory was not found.", 404

@app.route('/document/<document_name>')
def generate_document(document_name):
    """Generates a multi-page document with data from a JSON file."""
    document_dir = os.path.join(REPORTS_PATH, document_name)
    if not os.path.isdir(document_dir):
        abort(404)

    # Load data from data.json if it exists
    data_path = os.path.join(document_dir, 'data.json')
    document_data = {}
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            document_data = json.load(f)

    # Load custom CSS if it exists and render it with document_data
    custom_css_path = os.path.join(document_dir, 'style.css')
    custom_css = None
    if os.path.exists(custom_css_path):
        with open(custom_css_path, 'r', encoding='utf-8') as f:
            custom_css = render_template_string(f.read(), document_data=document_data)

    pages_content = []
    try:
        page_files = sorted([f for f in os.listdir(document_dir) if f.startswith('page') and f.endswith('.html')])
        for page_file in page_files:
            with open(os.path.join(document_dir, page_file), 'r', encoding='utf-8') as f:
                # Pass document_data to be rendered in each page fragment
                page_html = render_template_string(f.read(), document_data=document_data)
                pages_content.append(page_html)
    except FileNotFoundError:
        abort(404)

    documents = [d for d in os.listdir(REPORTS_PATH) if os.path.isdir(os.path.join(REPORTS_PATH, d))]
    return render_template(
        'base.html',
        pages=pages_content,
        custom_css=custom_css,
        documents=documents,
        current_document=document_name
    )

@app.route('/document/<document_name>/raw_html')
def raw_document_html(document_name):
    """
    Devuelve solo el HTML del documento.
    """
    document_dir = os.path.join(REPORTS_PATH, document_name)
    if not os.path.isdir(document_dir):
        abort(404)

    # Lee los fragmentos de página (sin procesar)
    page_files = sorted([f for f in os.listdir(document_dir) if f.startswith('page') and f.endswith('.html')])
    pages_raw = []
    for page_file in page_files:
        with open(os.path.join(document_dir, page_file), 'r', encoding='utf-8') as f:
            raw_content = f.read()
            embedded_content = _embed_images_as_base64(raw_content)
            pages_raw.append(embedded_content)
    pages_html = "\n".join(f'<div class="pagina">\n{page}\n</div>' for page in pages_raw)

    # Lee el base.html como texto
    base_path = os.path.join(TEMPLATES_PATH, 'base.html')
    with open(base_path, 'r', encoding='utf-8') as f:
        base_text = f.read()

    # Elimina todos los tags de Jinja de la base
    base_text = re.sub(r'{[{%].*?[%}]}', '', base_text, flags=re.DOTALL)

    # Reemplaza el bloque de páginas por el HTML de las páginas
    base_text = re.sub(
        r'(<div class="pagina-container">)(.*?)(</div>)',
        lambda m: f'{m.group(1)}\n{pages_html}\n{m.group(3)}',
        base_text,
        flags=re.DOTALL
    )

    markdown_content = f"""# Código HTML del Documento: {document_name}

## HTML
```html
{base_text.strip()}
```
"""
    response = make_response(markdown_content.strip())
    response.headers['Content-Type'] = 'text/markdown; charset=utf-8'
    return response

@app.route('/document/<document_name>/raw_css')
def raw_document_css(document_name):
    """
    Devuelve solo el CSS combinado del documento (global + custom).
    """
    document_dir = os.path.join(REPORTS_PATH, document_name)
    if not os.path.isdir(document_dir):
        abort(404)

    # Lee el CSS global como texto puro
    css_global_path = os.path.join('static', 'css', 'main.style.css')
    with open(css_global_path, 'r', encoding='utf-8') as f:
        css_global = f.read()

    custom_css_path = os.path.join(document_dir, 'style.css')
    css_custom = ''
    if os.path.exists(custom_css_path):
        with open(custom_css_path, 'r', encoding='utf-8') as f:
            css_custom = f.read()
    css_full = css_global
    if css_custom:
        css_full += "\n\n" + css_custom

    markdown_content = f"""# CSS del Documento: {document_name}

## CSS
```css
{css_full.strip()}
```
"""
    response = make_response(markdown_content.strip())
    response.headers['Content-Type'] = 'text/markdown; charset=utf-8'
    return response

def _render_highlighted_view(title, code, language):
    """
    Helper function to render a view with syntax-highlighted code.
    """
    markdown_content = f"""# {title}

```{language}
{code.strip()}
```
"""
    # Convierte el Markdown a HTML, Pygments se encargará de los bloques de código
    html_content = markdown_parser(markdown_content)
    # Genera el CSS necesario para el estilo de resaltado 'colorful'
    pygments_css = HtmlFormatter(style='colorful').get_style_defs('.highlight')

    # Renderiza la plantilla de vista raw con el contenido y los estilos
    return render_template('raw_view.html', title=title, content=html_content, pygments_css=pygments_css)

@app.route('/document/<document_name>/highlighted_html')
def highlighted_document_html(document_name):
    """
    Devuelve una vista HTML con el código fuente del documento resaltado.
    """
    document_dir = os.path.join(REPORTS_PATH, document_name)
    if not os.path.isdir(document_dir):
        abort(404)

    page_files = sorted([f for f in os.listdir(document_dir) if f.startswith('page') and f.endswith('.html')])
    pages_raw = []
    for pf in page_files:
        with open(os.path.join(document_dir, pf), 'r', encoding='utf-8') as f:
            raw_content = f.read()
            pages_raw.append(_embed_images_as_base64(raw_content))
    pages_html = "\n".join(f'<div class="pagina">\n{page}\n</div>' for page in pages_raw)

    with open(os.path.join(TEMPLATES_PATH, 'base.html'), 'r', encoding='utf-8') as f:
        base_text = f.read()

    base_text = re.sub(r'{[{%].*?[%}]}', '', base_text, flags=re.DOTALL)
    base_text = re.sub(r'(<div class="pagina-container">)(.*?)(</div>)', lambda m: f'{m.group(1)}\n{pages_html}\n{m.group(3)}', base_text, flags=re.DOTALL)

    title = f"Código HTML: {document_name}"
    return _render_highlighted_view(title, base_text, 'html')

@app.route('/document/<document_name>/highlighted_css')
def highlighted_document_css(document_name):
    """
    Devuelve una vista HTML con el CSS combinado del documento resaltado.
    """
    document_dir = os.path.join(REPORTS_PATH, document_name)
    if not os.path.isdir(document_dir):
        abort(404)

    with open(os.path.join('static', 'css', 'main.style.css'), 'r', encoding='utf-8') as f:
        css_global = f.read()
    css_custom_path = os.path.join(document_dir, 'style.css')
    css_custom = open(css_custom_path, 'r', encoding='utf-8').read() if os.path.exists(css_custom_path) else ''
    css_full = f"{css_global}\n\n{css_custom}" if css_custom else css_global

    title = f"Código CSS: {document_name}"
    return _render_highlighted_view(title, css_full, 'css')

@app.route('/css/style.css')
def serve_css():
    """Serves the CSS file."""
    response = make_response(render_template('css/style.css.j2'))
    response.headers['Content-Type'] = 'text/css'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5001)