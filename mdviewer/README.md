# mdviewer - local server for markdown files

runtime dependencies:

- `flask`
- `markdown2`
- `pygments`

To regenerate syntax css:

```
pygmentize -S default -f html > static/pygments.css
```

dev dependencies:

- `sass`: `sudo npm install -g sass`

## TODO

- Fix tables: no wrapping and add horiz scroll
- Fix search of terms with special symbols like 'vector<int>'
- Fix performance/snappiness
