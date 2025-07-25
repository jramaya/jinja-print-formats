# Generador de Documentos con Jinja2 y Flask

Este es un proyecto base para crear documentos de múltiples páginas listos para imprimir, utilizando Flask como servidor web y Jinja2 como motor de plantillas. La estructura está diseñada para ser modular y fácilmente escalable.

## Características

- **Estructura Modular**: Separa la plantilla base, el contenido de cada página y los estilos CSS.
- **Generación Dinámica**: El servidor Flask detecta automáticamente nuevas carpetas de documentos y las muestra en la página de inicio.
- **CSS para Impresión**: Incluye estilos `@media print` para asegurar que los documentos se vean bien al imprimirlos.
- **Vista Previa en Navegador**: Permite visualizar el documento final renderizado con datos y estilos, tal como se vería antes de imprimir.
- **Simulación de ERPNext**: Incluye `frappe.style.css` para emular el entorno de los "Print Formats" de ERPNext, facilitando la creación de formatos con una apariencia familiar.
- **CSS Auxiliar para Impresión**: El archivo `main.style.css` contiene clases y estilos de reseteo para construir documentos listos para imprimir.
- **Datos Dinámicos por Documento**: Carga datos desde un archivo `data.json` específico para cada documento, permitiendo que el contenido sea totalmente dinámico.
- **Vistas de Código Fuente**: Proporciona vistas del código HTML y CSS de cada documento, tanto en formato de texto plano (`raw`) como con resaltado de sintaxis para una mejor legibilidad.
- **Incrustación Automática de Imágenes**: Las imágenes referenciadas desde la carpeta `static/` se convierten automáticamente a base64 y se incrustan en el HTML, asegurando que el documento sea autocontenido y portátil.
- **Fácil de Extender**: Añadir un nuevo documento es tan simple como crear una nueva carpeta y sus archivos HTML de contenido.

## Estructura del Proyecto

```
.
├── app.py                 # Script de Python con Flask para servir la aplicación
├── static/
│   └── css/
│       ├── frappe.style.css # Estilos base para simular el entorno de impresión de ERPNext
│       └── main.style.css   # Hoja de estilos global para ajustes y personalizaciones
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
- **`templates/documents/[nombre-documento]/data.json`**: (Opcional) Un archivo JSON que contiene los datos a inyectar en las plantillas del documento. Estos datos están disponibles en tus plantillas `pageN.html` bajo la variable `doc`.
- **`templates/documents/`**: El directorio que contiene todos los documentos. Cada subdirectorio aquí es considerado un documento individual.

## Vistas Raw

En la página de inicio, cada documento tiene dos enlaces:
- **Ver HTML**: `/document/<nombre_documento>/raw_html`  
  Muestra el HTML del documento con la estructura base ya resuelta (sin tags Jinja en la base), pero los fragmentos de página insertados tal cual, con sus tags Jinja para `doc` intactos (por ejemplo, verás `{% for section in doc.sections %}` y `{{ section.title }}` en el HTML).
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
4.  (Opcional) Crea un archivo `data.json` en la misma carpeta. Dentro de este archivo, define la estructura de datos que necesites. Estos datos estarán disponibles en tus plantillas `pageN.html` a través del objeto `doc`. Por ejemplo: `{{ doc.titulo }}`.
5.  Cada uno de los archivos `pageN.html` solo debe contener el fragmento de HTML del contenido de esa página (títulos, párrafos, tablas, etc.), sin el `<html>` o `<body>`, y puede usar la sintaxis de Jinja2 para mostrar los datos del `data.json`.
6.  (Opcional) Si necesitas estilos personalizados para el documento, agrega un archivo `style.css` en la carpeta del documento.
7.  ¡Listo! Refresca la página de inicio en tu navegador y verás tu nuevo documento en la lista.
   Haz clic en el nombre del documento para ver la vista previa renderizada.

## Impresión Adaptativa

Es posible configurar los estilos para que el contenido se adapte al tamaño del papel de forma automática, utilizando unidades relativas como `vw` (viewport width). Esto es útil para que el tamaño de la fuente se ajuste si se imprime en A4, A5 o Carta.

Para lograrlo, puedes agregar los siguientes estilos en el `style.css` de tu documento:

```css
    #contenedor .pagina {
        width: fit-content;
        font-size: 1.4vw; /* tamano de fuente deseado */
        min-height: fit-content;
        height: fit-content;
        background-color: white;
    } 
```

Esto hará que el contenedor de la página se ajuste al contenido y que la fuente escale con el ancho del área de impresión.