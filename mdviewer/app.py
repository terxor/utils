import os
import sys
from flask import Flask, render_template, request, send_from_directory
from markupsafe import Markup
import markdown

app = Flask(__name__)
ROOT_DIR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()

def build_tree(start_path):
    tree = []
    for entry in sorted(os.listdir(start_path)):
        full_path = os.path.join(start_path, entry)
        rel_path = os.path.relpath(full_path, ROOT_DIR)
        if os.path.isdir(full_path):
            tree.append({
                'type': 'directory',
                'name': entry,
                'children': build_tree(full_path)
            })
        elif entry.endswith('.md'):
            tree.append({
                'type': 'file',
                'name': entry,
                'path': rel_path
            })
    return tree

@app.route('/', defaults={'filepath': ''})
@app.route('/<path:filepath>')
def index(filepath):
    tree = build_tree(ROOT_DIR)
    return render_template('index.html', tree=tree, filepath=filepath)

@app.route('/content')
def view_file():
    rel_path = request.args.get('file')
    abs_path = os.path.abspath(os.path.join(ROOT_DIR, rel_path))
    if not abs_path.startswith(ROOT_DIR):
        return "Access denied", 403
    if not os.path.isfile(abs_path):
        return "File not found", 404

    with open(abs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    html = markdown.markdown(content, extensions=['tables', 'extra'])
    return html

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
