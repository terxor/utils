#!/usr/bin/python3

import os
import argparse
from flask import Flask, render_template, request, send_from_directory, jsonify, abort
from markupsafe import Markup
import markdown2
import re
from urllib.parse import urlparse
from fuzzy_search import FuzzySearch

def strip_self_links(html: str) -> str:
    def replacer(match):
        url = match.group(1)
        parsed = urlparse(url)
        label = parsed.netloc + parsed.path
        return f'<a href="{url}">{label}</a>'
    return re.sub(
        r'<a\s+href=["\'](http[s]?://[^"\']+)["\']>\s*\1\s*</a>',
        replacer,
        html
    )

class MarkdownViewer:
    def __init__(self, root_dir, enable_math=False, debug=False):
        self.root_dir = os.path.abspath(root_dir)
        self.enable_math = enable_math
        self.debug = debug
        self.app = Flask(__name__)
        self.fuzzy_search = FuzzySearch()
        self.setup_routes()
        self.index_files()

    def index_files(self):
        self.fuzzy_search.index_directory(self.root_dir)

    def build_tree(self, start_path):
        ignored_dirs = {'.git', '__pycache__'}
        tree = []
        for entry in sorted(os.listdir(start_path)):
            if entry in ignored_dirs:
                continue
            full_path = os.path.join(start_path, entry)
            rel_path = os.path.relpath(full_path, self.root_dir)
            if os.path.isdir(full_path):
                children = self.build_tree(full_path)
                if children:
                    tree.append({
                        'type': 'directory',
                        'name': entry,
                        'children': children
                    })
            elif entry.endswith('.md'):
                tree.append({
                    'type': 'file',
                    'name': entry,
                    'path': rel_path
                })
        return tree
    
    def clean_math(self, content):
        # Merge all lines inside $$...$$, remove leading > and whitespace from each line
        def replacer(m):
            inner = m.group(1)
            # Remove leading > and spaces from each line
            lines = [re.sub(r'^\s*>?\s?', '', line) for line in inner.splitlines()]
            merged = ' '.join(lines)
            return '$$' + merged.replace('\\', '\\\\') + '$$'
        content = re.sub(r'\$\$(.*?)\$\$', replacer, content, flags=re.DOTALL)
        return content

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
            if self.enable_math:
                content = self.clean_math(content)
            html = markdown2.markdown(content, extras=[
                "fenced-code-blocks",
                "code-friendly",
                "code-color",
                "tables",
                "cuddled-lists",
            ])
            html = strip_self_links(html)
            return html

        @self.app.route('/static/<path:path>')
        def send_static(path):
            return send_from_directory('static', path)

        @self.app.route('/search', methods=['GET'])
        def search():
            query = request.args.get('query', '')
            if not query:
                return jsonify([])
            words = [w for w in query.strip().split() if w]
            results = self.fuzzy_search.context_search(words)
            return jsonify(results)

        @self.app.route('/refresh_index', methods=['POST'])
        def refresh_index():
            self.index_files()
            return jsonify({"message": "Index refreshed successfully."})

        @self.app.route('/api/tree')
        def api_tree():
            tree = self.build_tree(self.root_dir)
            return jsonify(tree)

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
