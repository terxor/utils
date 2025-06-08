// Pre-loaded constants: enable_math, filepath

const CSS_CLASS = {
  TREE: 'tree',
  TREE_ENTRY: 'tree-entry',
  TREE_DIR: 'tree-dir',
  TREE_FILE: 'tree-file',
  TREE_COLLAPSED: 'tree-collapsed',
  TEMP_HIGHLIGHT: 'temp-highlight',
  TOC_LINK: 'toc-link',
  SIDEBAR: 'sidebar',
  NESTED: 'nested',
  ACTIVE: 'active'
};

const CONSTANTS = {
  TOC_HIGHLIGHT_DURATION: 1000, // ms
  CONTENT_HIGHLIGHT_DURATION: 5000,
}

function renderTreeHTML(tree, parentUl, depth = 0) {
  tree.forEach(item => {
    if (!item.name || typeof item.onClick !== 'function') {
      console.error("Invalid tree item:", item);
      return;
    }

    const li = document.createElement('li');
    li.classList.add(CSS_CLASS.TREE);

    if (item.collapsed) {
      li.classList.add(CSS_CLASS.TREE_COLLAPSED);
    }

    const entry = document.createElement('a');
    entry.classList.add(CSS_CLASS.TREE_ENTRY);
    entry.textContent = item.name;
    entry.style.setProperty('--tree-depth', depth);

    // Revert: Always allow clicking, just highlight current file
    if (
      item.dataPath &&
      typeof filepath !== "undefined" &&
      filepath !== "" &&
      item.dataPath === filepath
    ) {
      entry.classList.add('current-file');
      entry.setAttribute('aria-current', 'page');
      // No pointerEvents or opacity changes
    }
    entry.addEventListener('click', item.onClick);

    // Set data-path for file entries
    if (item.dataPath) {
      entry.setAttribute('data-path', item.dataPath);
    }

    // Set href for TOC entries
    if (item.href) {
      entry.setAttribute('href', item.href);
    }

    li.appendChild(entry);

    if (item.children && item.children.length) {
      const ul = document.createElement('ul');
      ul.classList.add(CSS_CLASS.NESTED);
      renderTreeHTML(item.children, ul, depth + 1);
      li.appendChild(ul);
    }
    parentUl.appendChild(li);
  });
}

function addTempHighlight(el, duration = 4000, transitionMs = 1000) {
  if (!el) return;
  el.classList.add(CSS_CLASS.TEMP_HIGHLIGHT);
  // Ensure transition is set (in case CSS is missing/overridden)
  el.style.transition = `background ${transitionMs}ms, box-shadow ${transitionMs}ms`;
  setTimeout(() => {
    el.classList.add('fading');
    setTimeout(() => {
      el.classList.remove(CSS_CLASS.TEMP_HIGHLIGHT, 'fading');
      el.style.transition = ''; // Clean up inline style
    }, transitionMs);
  }, duration);
}

function buildTOCTree(headings) {
  const root = [];
  const stack = [{level: 0, children: root}];

  headings.forEach((h, idx) => {
    const level = parseInt(h.tagName[1]);
    h.id = `toc-h${level}-${idx}`;
    const node = {
      name: h.textContent,
      children: [],
      onClick: function(e) {
        e.preventDefault();
        const target = document.getElementById(h.id);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          addTempHighlight(target, CONSTANTS.TOC_HIGHLIGHT_DURATION, 300);
        }
      },
      collapsed: false,
      href: `#${h.id}` // Add href for TOC highlighting
    };
    while (stack.length && stack[stack.length - 1].level >= level) stack.pop();
    stack[stack.length - 1].children.push(node);
    stack.push({level, children: node.children});
  });

  return root;
}

// Helper to expand and highlight the current file in the directory tree
function highlightCurrentFileInTree(filepath) {
  const root = document.getElementById('dir-tree-root');
  if (!root) return;
  // Remove previous highlights
  root.querySelectorAll('.tree-entry.active').forEach(el => el.classList.remove('active'));

  // Find the file entry
  const fileEntry = root.querySelector(`.tree-entry[data-path="${filepath}"]`);
  if (fileEntry) {
    fileEntry.classList.add('active');
    // Expand all parent directories
    let li = fileEntry.closest('li');
    while (li) {
      li.classList.remove(CSS_CLASS.TREE_COLLAPSED);
      li = li.parentElement.closest('li');
    }
    // Scroll into view if not visible
    fileEntry.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }
}

// Helper to highlight the TOC entry for the current scroll position
function highlightCurrentTOCOnScroll() {
  const headings = Array.from(document.querySelectorAll('#markdown-body h1, #markdown-body h2, #markdown-body h3, #markdown-body h4, #markdown-body h5, #markdown-body h6'));
  const tocRoot = document.getElementById('toc-container');
  if (!headings.length || !tocRoot) return;

  tocRoot.querySelectorAll('.tree-entry.active').forEach(el => el.classList.remove('active'));

  let current = headings[0];
  const scrollY = window.scrollY || window.pageYOffset;
  const threshold = 40; // px from top

  for (const h of headings) {
    const hTop = h.getBoundingClientRect().top + scrollY;
    if (hTop - scrollY <= threshold) {
      current = h;
    } else {
      break;
    }
  }

  if (current && current.id) {
    const tocEntry = tocRoot.querySelector(`.tree-entry[href="#${current.id}"]`);

    if (tocEntry) {
      tocEntry.classList.add('active');
      // Only scroll if not fully visible in the viewport
      const entryRect = tocEntry.getBoundingClientRect();
      const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
      if (
        entryRect.top < 0 ||
        entryRect.bottom > viewportHeight
      ) {
        tocEntry.scrollIntoView({ block: "center", behavior: "auto" });
      }
    }

  }
}

function enrichDirTree(tree) {
  return tree.map(item => {
    if (item.type === 'directory') {
      return {
        ...item,
        onClick: function(e) {
          const li = this.parentNode;
          li.classList.toggle(CSS_CLASS.TREE_COLLAPSED);
          e.stopPropagation();
        },
        children: enrichDirTree(item.children || []),
        collapsed: true // Start directories collapsed
      };
    } else {
      return {
        ...item,
        onClick: function(e) {
          fetchContent(item.path, "");
          e.stopPropagation();
        },
        collapsed: false, // Files are not collapsible
        dataPath: item.path // Add this for later use
      };
    }
  });
}

// Generate a 3-level TOC (H1/H2/H3) from the rendered markdown in #viewer
function generateTOC() {
  const viewer = document.getElementById('markdown-body');
  const tocContainer = document.getElementById('toc-container');
  if (!viewer || !tocContainer) return;

  const headings = viewer.querySelectorAll('h1, h2, h3, h4, h5, h6');
  if (!headings.length) {
    return;
  }
  const tocTree = buildTOCTree(headings);
  const ul = document.createElement('ul');
  ul.classList.add(CSS_CLASS.TREE);
  renderTreeHTML(tocTree, ul);
  tocContainer.innerHTML = '';
  tocContainer.appendChild(ul);
}

// Add copy-to-clipboard buttons for code blocks
const genCopyButtons = () => {
  document.querySelectorAll('pre > code').forEach(codeBlock => {
    const pre = codeBlock.parentNode;
    pre.addEventListener('click', () => {
      const selection = window.getSelection();
      if (selection && selection.toString().length > 0) return; // Don't copy if selecting
      navigator.clipboard.writeText(codeBlock.innerText).then(() => {
        pre.classList.add('copied');
        setTimeout(() => pre.classList.remove('copied'), 400);
      });
    });
  });
};

// Fetch and display file content, now accepts contextBlock
const fetchContent = (fp, highlightWord, lineno, contextBlock) => {
  fetch('/content?file=' + encodeURIComponent(fp))
    .then(res => res.text())
    .then(html => {
      console.time('renderMarkdown');

      const viewer = document.getElementById('markdown-body');
      viewer.innerHTML = html;

      if (highlightWord === undefined || highlightWord === null || highlightWord === "") {
        highlightWord = ""; // Default to empty string if not provided
        // Wait for DOM update, then scroll to top
        requestAnimationFrame(() => {
          window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
        });
      }

      if (enable_math) {
        renderMathInElement(viewer, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '\\[', right: '\\]', display: true },
            { left: '$', right: '$', display: false },
            { left: '\\(', right: '\\)', display: false }
          ],
          throwOnError: false
        });
      }
      history.pushState({}, '', '/' + fp);
      document.title = fp;
      genCopyButtons();
      generateTOC();
      highlightCurrentFileInTree(fp);

      // 1. Highlight all query words
      if (highlightWord) highlightWordInViewer(highlightWord, contextBlock);

      console.timeEnd('renderMarkdown');
    });
};

// Utility to highlight all occurrences of query words (case-insensitive, partial matches)
function highlightMatches(text, query) {
  if (!query) return text;
  const words = query
    .split(/\s+/)
    .filter(Boolean)
    .map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  if (words.length === 0) return text;
  const regex = new RegExp(`(${words.join('|')})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}

// Unified search: searches both file names and content, but does NOT touch the directory tree display
function setupUnifiedSearch() {
  const input = document.getElementById('search-input');
  const resultsPanel = document.getElementById('search-results');
  const fileResults = document.getElementById('search-results-file');
  const contentResults = document.getElementById('search-results-content');
  let debounceTimer = null;
  const CONTEXT_BLOCK_SIZE = 5; // Number of lines in a context block

  function positionPanel() {
    const rect = input.getBoundingClientRect();
    resultsPanel.style.left = rect.left + window.scrollX + "px";
    resultsPanel.style.top = (rect.bottom + window.scrollY + 4) + "px";
    resultsPanel.style.width = Math.max(600, rect.width, window.innerWidth * 0.7) + "px";
    resultsPanel.style.maxWidth = "1200px";
    resultsPanel.style.transform = ""; // Remove center transform
  }

  input.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      const query = input.value.trim();
      fileResults.innerHTML = '';
      contentResults.innerHTML = '';
      if (!query) {
        resultsPanel.style.display = 'none';
        return;
      }
      positionPanel();
      resultsPanel.style.display = 'block';

      // 1. Local file name search
      fetch('/api/tree')
        .then(res => res.json())
        .then(tree => {
          const files = [];
          function walk(node) {
            node.forEach(item => {
              if (item.type === 'file') files.push(item);
              else if (item.type === 'directory') walk(item.children);
            });
          }
          walk(tree);
          const localMatches = files.filter(f => f.path.toLowerCase().includes(query.toLowerCase()));

          if (localMatches.length === 0) {
            fileResults.innerHTML = '<li style="color:#888;padding:0.5em;">No files found.</li>';
          } else {
            localMatches.forEach(item => {
              const li = document.createElement('li');
              // Highlight the path, not just the name
              li.innerHTML = `<span class="file" data-path="${item.path}">${highlightMatches(item.path, query)}</span>`;
              li.style.cursor = 'pointer';
              li.onclick = () => {
                fetchContent(item.path, ""); // No context block for file name search
                resultsPanel.style.display = 'none';
                input.value = '';
              };
              fileResults.appendChild(li);
            });
          }

          // 2. Global content/context search
          fetch(`/search?query=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(globalResults => {
              if (globalResults.length === 0) {
                contentResults.innerHTML = '<li style="color:#888;padding:0.5em;">No content found.</li>';
              } else {
                globalResults.forEach(item => {
                  const li = document.createElement('li');
                  li.innerHTML = `<div>
                    <strong>${highlightMatches(item.path, query)}</strong>
                    <pre style="font-size:smaller;color:#555;margin-top:2px;">${highlightMatches(
                      item.preview.replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c])),
                      query
                    )}</pre>
                  </div>`;
                  li.style.cursor = 'pointer';
                  li.onclick = () => {
                    fetchContent(item.path, query, null, item.preview); // Pass context block!
                    resultsPanel.style.display = 'none';
                    input.value = '';
                  };
                  contentResults.appendChild(li);
                });
              }
            });
        });
    }, 300);
  });

  // Hide results when clicking outside
  document.addEventListener('click', (e) => {
    if (!resultsPanel.contains(e.target) && e.target !== input) {
      resultsPanel.style.display = 'none';
    }
  });

  // Hide on Escape
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      resultsPanel.style.display = 'none';
      input.value = '';
    }
  });

  // Reposition on window resize/scroll
  window.addEventListener('resize', () => {
    if (resultsPanel.style.display === 'block') positionPanel();
  });
  window.addEventListener('scroll', () => {
    if (resultsPanel.style.display === 'block') positionPanel();
  });
}

// Load and render directory tree from API
function loadAndRenderTree() {
  fetch('/api/tree')
    .then(res => res.json())
    .then(tree => {
      const root = document.getElementById('dir-tree-root');
      root.innerHTML = '';
      const ul = document.createElement('ul');
      ul.classList.add(CSS_CLASS.TREE);
      tree = enrichDirTree(tree);
      renderTreeHTML(tree, ul);
      root.appendChild(ul);
      if (typeof filepath !== "undefined" && filepath !== "") {
        highlightCurrentFileInTree(filepath);
      }
    });
}

// Listen for scroll to highlight current TOC entry
window.addEventListener('scroll', () => {
  highlightCurrentTOCOnScroll();
});

// Initialize everything on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  loadAndRenderTree();
  setupUnifiedSearch();
  if (typeof filepath !== "undefined" && filepath !== "") {
    fetchContent(filepath);
  }
});
