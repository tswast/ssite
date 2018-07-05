# Ssite

Ssite is not a static site generator. It is a collection of scripts to
maintain a static site. All build steps are optional; the source code for a
static site that uses Ssite is hostable without any modifications.

## Installation

```
pip install --upgrade ssite
```

## Usage

`ssite index` generates an index file for a collection of timestamped
HTML documents.

`ssite clean` removes `style`, `class`, and `id`, `<span>` and other
messy markup from an HTML document.

## License

Licensed under Apache License, Version 2.0. See
[LICENSE](https://github.com/tswast/ssite/blob/master/LICENSE).
