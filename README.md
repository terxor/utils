# utils: General utilities

## `dfx` - Data Format eXchange

To transform data from one format to another. This is meant for plaintext,
lightweight usage.

Two formats are supported:

- CSV
- Markdown tabular format

### Examples

Input file `infile`:

```
key,value
a,5
b,6
c,7
```

Command:

```
dfx --from csv --to md < infile
```

Output:

```
| key | value |
| --- | ----- |
| a   | 5     |
| b   | 6     |
| c   | 7     |
```

Transformation from MD to CSV, naturally, is also possible.

One can use the following command to reformat a MD table:

```
dfx --from md --to md
```

Conversions including type parsing are also possible
using the `--parse-types` flag, for example:

Input file `infile`:

```
key,value
a,5.000
b,6e2
c,7
```

Output:

```
dfx --from csv --to md --parse-types < infile
| key | value |
| --- | ----- |
| a   | 5     |
| b   | 600   |
| c   | 7     |
```

A feature particularly for terminals, and only supported for markdown
format is colors. One can specify output colors by a series of rules
of form `[<row range>][<col range>]=<color>`, for example:

```
dfx --from csv --to md --parse-types --md-colors "[2:][]=red,[3][2]=green" < $tb/a
```

Would effectively color rows 2 to end as red (all columns), then overwrite
cell 3,2 with color green.

Other flags:

- `--md-no-header`: Do not print header (first 2 lines) in md format
- `--tf-backtick`: Accepts list of 1-index comma separated columns and adds a
  surrounds the contents by backticks. Useful for markdown representation.

--------------------------------------------------------------------------------

## `textquery` - SQL on plaintext data

TODO

--------------------------------------------------------------------------------

## `timestamp` - Standard timestamps from flexible input

TODO

--------------------------------------------------------------------------------

## `tmpbuf` - Temporary Buffers

TODO

--------------------------------------------------------------------------------
