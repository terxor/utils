#!/usr/bin/python3

import os
import sys, argparse
from flask import Flask, render_template, request, send_from_directory
from markupsafe import Markup
import markdown2

class MarkdownViewer:
    def __init__(self, root_dir, enable_math=False, debug=False):
        self.root_dir = os.path.abspath(root_dir)
        self.enable_math = enable_math
        self.debug = debug
        self.app = Flask(__name__)
        self.setup_routes()

    def build_tree(self, start_path):
        ignored_dirs = {'.git', '__pycache__'}
        tree = []
        for entry in sorted(os.listdir(start_path)):
            if entry in ignored_dirs:
                continue
            full_path = os.path.join(start_path, entry)
            rel_path = os.path.relpath(full_path, self.root_dir)
            if os.path.isdir(full_path):
                tree.append({
                    'type': 'directory',
                    'name': entry,
                    'children': self.build_tree(full_path)
                })
            elif entry.endswith('.md'):
                tree.append({
                    'type': 'file',
                    'name': entry,
                    'path': rel_path
                })
        return tree

    def setup_routes(self):
        @self.app.route('/', defaults={'filepath': ''})
        @self.app.route('/<path:filepath>')
        def index(filepath):
            tree = self.build_tree(self.root_dir)
            return render_template('index.html', tree=tree, filepath=filepath, enable_math=self.enable_math)

        @self.app.route('/content')
        def view_file():
            rel_path = request.args.get('file')
            if not rel_path:
                return "Missing file path", 400
            abs_path = os.path.abspath(os.path.join(self.root_dir, rel_path))
            if not abs_path.startswith(self.root_dir) or not os.path.isfile(abs_path):
                abort(403)
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            html = markdown2.markdown(content, extras=[
                "fenced-code-blocks",   # for triple backticks
                "code-friendly",        # don't mangle code indentation
                "code-color",
                "tables",               # GitHub-style tables
                "cuddled-lists",        # tighter list/paragraph rendering
            ])
            return html  # template will handle math if enabled

        @self.app.route('/static/<path:path>')
        def send_static(path):
            return send_from_directory('static', path)

    def run(self):
        self.app.run(debug=self.debug)

def main():
    parser = argparse.ArgumentParser(description="Markdown viewer with optional math rendering")
    parser.add_argument("directory", help="Directory to serve")
    parser.add_argument("--math", action="store_true", help="Enable MathJax for LaTeX-style math")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    viewer = MarkdownViewer(root_dir=args.directory, enable_math=args.math, debug=args.debug)
    viewer.run()

if __name__ == '__main__':
    main()
