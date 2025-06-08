function highlightWordInViewer(query, context) {
  // console.log('highlightWordInViewer query:', query);
  // console.log('highlightWordInViewer context:', context);
  if (!query) return;
  const viewer = document.getElementById('markdown-body');
  if (!viewer) return;

  // Prepare search and context words
  const searchWords = query
    .split(/\s+/)
    .filter(Boolean)
    .map(w => w.toLowerCase());
  if (searchWords.length === 0) return;

  const contextWords = context
    ? context.replace(/[^\w\s]|_/g, '').toLowerCase().split(/\s+/).filter(Boolean)
    : [];

  // console.log('searchWords:', searchWords);
  // console.log('contextWords:', contextWords);

  // Gather all blocks
  let blocks = Array.from(viewer.querySelectorAll(
    'p, li, pre, div, h1, h2, h3, h4, h5, h6, tr, td, th'
  ));

  // Find the window of consecutive blocks containing the most context words in order
  let bestWindow = [0, 0];
  let bestScore = -1;
  const maxWindow = 5;

  if (contextWords.length) {
    // Pre-normalize block texts
    const blockNorms = blocks.map(
      b => b.innerText.replace(/[^\w\s]|_/g, '').toLowerCase().split(/\s+/).filter(Boolean)
    );
    // console.log('blockNorms:', blockNorms);
    for (let start = 0; start < blocks.length; ++start) {
      let joined = [];
      for (let end = start; end < Math.min(blocks.length, start + maxWindow); ++end) {
        joined = joined.concat(blockNorms[end]);
        // Score: count of context words found in order in joined
        let score = countOrderedMatch(contextWords, joined, searchWords);
        if (score > bestScore) {
          bestScore = score;
          bestWindow = [start, end];
        }
        // Early exit if perfect match
        if (score === contextWords.length) break;
      }
      if (bestScore === contextWords.length) break;
    }
    blocks = blocks.slice(bestWindow[0], bestWindow[1] + 1);
  } else {
    blocks = [viewer];
  }

  // console.log('bestWindow:', bestWindow);
  // console.log('bestScore:', bestScore);
  // console.log('blocks:', blocks.map(b => b.innerText.trim()));

  // Highlight search words in the best window
  blocks.forEach(block => {
    const textNodes = [];
    function collectTextNodes(node) {
      if (node.nodeType === 3 && node.nodeValue.trim()) {
        textNodes.push({node, text: node.nodeValue, parent: node.parentNode});
      } else if (node.nodeType === 1 && !['SCRIPT', 'STYLE', 'SPAN'].includes(node.tagName)) {
        Array.from(node.childNodes).forEach(collectTextNodes);
      }
    }
    collectTextNodes(block);

    textNodes.forEach(t => {
      let text = t.text;
      let replaced = false;
      let parts = [];
      let lastIdx = 0;
      let regex = new RegExp(searchWords.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'gi');
      let match;
      while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIdx) {
          parts.push(document.createTextNode(text.slice(lastIdx, match.index)));
        }
        const span = document.createElement('span');
        span.textContent = match[0];
        addTempHighlight(span, 4000, 700);
        parts.push(span);
        lastIdx = regex.lastIndex;
        replaced = true;
      }
      if (replaced) {
        if (lastIdx < text.length) {
          parts.push(document.createTextNode(text.slice(lastIdx)));
        }
        const frag = document.createDocumentFragment();
        parts.forEach(p => frag.appendChild(p));
        if (t.node.parentNode) t.node.parentNode.replaceChild(frag, t.node);
      }
    });
  });

  // Scroll to the first .temp-highlight in any of the blocks
  let first = null;
  for (const block of blocks) {
    first = block.querySelector('.temp-highlight');
    if (first) break;
  }
  if (first) {
    first.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

// Helper: count how many contextWords appear in order in joinedWords,
// but only if all searchWords are present in joinedWords
function countOrderedMatch(contextWords, joinedWords, searchWords) {
  // Prerequisite: all searchWords must be present in joinedWords
  for (const word of searchWords) {
    if (!joinedWords.some(w => w.includes(word))) return 0;
  }
  // Count how many contextWords appear in order in joinedWords
  let i = 0, j = 0, count = 1;
  while (i < contextWords.length && j < joinedWords.length) {
    if (contextWords[i] === joinedWords[j]) {
      count++;
      i++;
    }
    j++;
  }
  return count;
}