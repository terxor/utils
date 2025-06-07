import re
import os

class FuzzySearch:
    def __init__(self):
        self.file_index = []
        self.file_contents = {}

    def index_directory(self, root_dir):
        self.file_index = []
        self.file_contents = {}
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.md'):
                    rel_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
                    self.file_index.append(rel_path)
                    try:
                        with open(os.path.join(dirpath, filename), 'r', encoding='utf-8') as f:
                            self.file_contents[rel_path] = f.read()
                    except Exception:
                        self.file_contents[rel_path] = ""

    def get_relevant_preview(self, content, query, preview_len=80):
        if not query or not content:
            return content[:preview_len]
        words = [re.escape(w) for w in query.strip().split() if w]
        if not words:
            return content[:preview_len]
        pattern = re.compile(r'(' + '|'.join(words) + r')', re.IGNORECASE)
        match = pattern.search(content)
        if match:
            start = max(match.start() - preview_len // 2, 0)
            end = min(start + preview_len, len(content))
            snippet = content[start:end]
            if start > 0:
                snippet = '...' + snippet
            if end < len(content):
                snippet = snippet + '...'
            if snippet.strip('.') == '':
                return content[:preview_len]
            return snippet
        else:
            return content[:preview_len]

    def search(self, query, limit=10):
        query = query.strip()
        if not query or ' ' in query:
            return []
        results = []
        word = re.escape(query)
        pattern = re.compile(rf'\b{word}\b', re.IGNORECASE)
        for path, content in self.file_contents.items():
            lines = content.splitlines()
            for idx, line in enumerate(lines):
                if pattern.search(line):
                    start = max(idx - 2, 0)
                    end = min(idx + 3, len(lines))
                    snippet = '\n'.join(lines[start:end])
                    results.append({
                        'path': path,
                        'preview': snippet,
                        'lineno': idx + 1
                    })
                    if len(results) >= limit:
                        return results
        return results

    def context_search(self, words, block_size=5, limit=20):
        """
        Return non-overlapping blocks of block_size lines containing ALL words (case-insensitive),
        with highlights applied to the preview.
        """
        results = []
        word_patterns = [re.compile(re.escape(w), re.IGNORECASE) for w in words]
        for path, content in self.file_contents.items():
            lines = content.splitlines()
            n = len(lines)
            i = 0
            while i <= n - block_size:
                block = lines[i:i+block_size]
                if all(any(p.search(line) for line in block) for p in word_patterns):
                    block_text = '\n'.join(block)
                    results.append({
                        'path': path,
                        'preview': block_text,
                        'lineno': i + 1
                    })
                    if len(results) >= limit:
                        return results
                    i += block_size
                else:
                    i += 1
        return results