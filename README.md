# Generador de Documentos con Jinja2 y Flask

Este es un proyecto base para crear documentos de múltiples páginas listos para imprimir, utilizando Flask como servidor web y Jinja2 como motor de plantillas. La estructura está diseñada para ser modular y fácilmente escalable.

## Características

- **Estructura Modular**: Separa la plantilla base, el contenido de cada página y los estilos CSS.
- **Generación Dinámica**: El servidor Flask detecta automáticamente nuevas carpetas de documentos y las muestra en la página de inicio.
- **CSS para Impresión**: Incluye estilos `@media print` para asegurar que los documentos se vean bien al imprimirlos.
- **Datos Dinámicos por Documento**: Carga datos desde un archivo `data.json` específico para cada documento, permitiendo que el contenido sea totalmente dinámico.
- **Vistas de Código Fuente**: Proporciona vistas del código HTML y CSS de cada documento, tanto en formato de texto plano (`raw`) como con resaltado de sintaxis para una mejor legibilidad.
- **Fácil de Extender**: Añadir un nuevo documento es tan simple como crear una nueva carpeta y sus archivos HTML de contenido.

## Estructura del Proyecto

```
.
├── app.py                 # Script de Python con Flask para servir la aplicación
├── static/
│   └── css/
│       └── main.style.css # Hoja de estilos global (CSS puro, no plantilla Jinja)
├── templates/
│   ├── base.html          # Plantilla HTML principal (esqueleto de la página)
│   ├── index.html         # Página de inicio que lista todos los documentos
│   └── documents/
│       └── Lorem-Ipsum-document/  # Carpeta para un documento específico
│           ├── data.json      # Datos en formato JSON para el documento
│           ├── page1.html     # Contenido de la primera página (con tags Jinja)
│           ├── page2.html     # Contenido de la segunda página (con tags Jinja)
│           └── style.css      # (Opcional) Estilos CSS específicos para este documento
└── README.md              # Este archivo
```

- **`app.py`**: El corazón de la aplicación. Contiene las rutas para la página de inicio, la generación de documentos y las vistas raw.
- **`static/css/main.style.css`**: La hoja de estilos global. Es un archivo CSS normal, no una plantilla Jinja.
- **`templates/base.html`**: La plantilla maestra. Define la estructura HTML común (el `head`, el `body`, el `pagina-container`) para todos los documentos. Carga el CSS global desde `/static/css/main.style.css`.
- **`templates/index.html`**: La página que se muestra en la raíz del sitio. Lista todos los directorios encontrados dentro de `templates/documents` y muestra enlaces para ver el HTML y CSS raw de cada documento.
- **`templates/documents/[nombre-documento]/data.json`**: (Opcional) Un archivo JSON que contiene los datos a inyectar en las plantillas del documento. Estos datos están disponibles en tus plantillas `pageN.html` bajo la variable `document_data`.
- **`templates/documents/`**: El directorio que contiene todos los documentos. Cada subdirectorio aquí es considerado un documento individual.

## Vistas Raw

En la página de inicio, cada documento tiene dos enlaces:
- **Ver HTML**: `/document/<nombre_documento>/raw_html`  
  Muestra el HTML del documento con la estructura base ya resuelta (sin tags Jinja en la base), pero los fragmentos de página insertados tal cual, con sus tags Jinja para `document_data` intactos (por ejemplo, verás `{% for section in document_data.sections %}` y `{{ section.title }}` en el HTML).
- **Ver CSS**: `/document/<nombre_documento>/raw_css`  
  Muestra el CSS combinado: primero el global y luego el custom del documento (si existe).

Ambas vistas se muestran en formato Markdown para facilitar la copia y revisión del código fuente.

## Cómo Empezar

### Prerrequisitos

- Tener Python 3 instalado.

### Instalación

1.  Clona o descarga este repositorio.
2.  Abre una terminal en el directorio del proyecto.
3.  (Opcional pero recomendado) Crea y activa un entorno virtual:
    ```bash
    python -m venv venv
    # En Windows
    venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```
4.  Instala las dependencias del proyecto:
    ```bash
    pip install -r requirements.txt
    ```

### Ejecución

1.  Desde la terminal, en el directorio raíz del proyecto, ejecuta el servidor de Flask:
    ```bash
    python app.py
    ```
2.  Abre tu navegador web y visita `http://127.0.0.1:5001/`.

## Cómo Crear un Nuevo Documento

1.  Ve al directorio `templates/documents/`.
2.  Crea una nueva carpeta con un nombre descriptivo para tu documento (por ejemplo, `Ventas-Anuales-2024`).
3.  Dentro de esa nueva carpeta, crea los archivos de contenido para cada página. Nómbralos secuencialmente para que se ordenen correctamente: `page1.html`, `page2.html`, etc.
4.  (Opcional) Crea un archivo `data.json` en la misma carpeta. Dentro de este archivo, define la estructura de datos que necesites. Estos datos estarán disponibles en tus plantillas `pageN.html` a través del objeto `document_data`. Por ejemplo: `{{ document_data.titulo }}`.
5.  Cada uno de los archivos `pageN.html` solo debe contener el fragmento de HTML del contenido de esa página (títulos, párrafos, tablas, etc.), sin el `<html>` o `<body>`, y puede usar la sintaxis de Jinja2 para mostrar los datos del `data.json`.
6.  (Opcional) Si necesitas estilos personalizados para el documento, agrega un archivo `style.css` en la carpeta del documento.
7.  ¡Listo! Refresca la página de inicio en tu navegador y verás tu nuevo documento en la lista.