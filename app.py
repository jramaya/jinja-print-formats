import os
import json
from flask import Flask, render_template, render_template_string, abort, make_response

app = Flask(__name__)

REPORTS_PATH = os.path.join('templates', 'reports')

@app.route('/')
def index():
    """Lists all available reports."""
    try:
        reports = [d for d in os.listdir(REPORTS_PATH) if os.path.isdir(os.path.join(REPORTS_PATH, d))]
        return render_template('index.html', reports=reports)
    except FileNotFoundError:
        return "The 'templates/reports' directory was not found.", 404

@app.route('/report/<report_name>')
def generate_report(report_name):
    """Generates a multi-page report with data from a JSON file."""
    report_dir = os.path.join(REPORTS_PATH, report_name)
    if not os.path.isdir(report_dir):
        abort(404)

    # Load data from data.json if it exists
    data_path = os.path.join(report_dir, 'data.json')
    report_data = {}
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

    # Load custom CSS if it exists and render it with report_data
    custom_css_path = os.path.join(report_dir, 'style.css')
    custom_css = None
    if os.path.exists(custom_css_path):
        with open(custom_css_path, 'r', encoding='utf-8') as f:
            custom_css = render_template_string(f.read(), report_data=report_data)

    pages_content = []
    try:
        page_files = sorted([f for f in os.listdir(report_dir) if f.startswith('page') and f.endswith('.html')])
        for page_file in page_files:
            with open(os.path.join(report_dir, page_file), 'r', encoding='utf-8') as f:
                # Pass report_data to be rendered in each page fragment
                page_html = render_template_string(f.read(), report_data=report_data)
                pages_content.append(page_html)
    except FileNotFoundError:
        abort(404)

    return render_template('base.html', pages=pages_content, custom_css=custom_css)

@app.route('/css/style.css')
def serve_css():
    """Serves the CSS file."""
    response = make_response(render_template('css/style.css.j2'))
    response.headers['Content-Type'] = 'text/css'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5001)