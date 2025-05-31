# mdviewer - local server for markdown files

dependencies:

- `flask`
- `markdown2`
- `pygments`

To regenerate syntax css:

```
pygmentize -S default -f html > static/pygments.css
```
