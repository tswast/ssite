# Ssite

Ssite is not a static site generator. It is a collection of scripts to
maintain a static site. All build steps are optional; the source code for a
static site that uses Ssite is hostable without any modifications.

[![PyPI](https://img.shields.io/pypi/v/ssite.svg)](https://pypi.org/project/ssite/)

## Installation

```
pip install --upgrade ssite
```

## Principles

* Enhance; don't generate.

Ssite works directly with the source and never creates separate build
directories. The source of your static site is always publishable without
ssite.

## Usage

`ssite index INDEXED_DIR` generates an index file for a collection of
timestamped HTML documents.

`ssite clean INPUT_PATH` removes `style`, `class`, and `id`, `<span>` and
other messy markup from an HTML document.

Help text is rendered using the argparse library.

`ssite --help` displays the list of commands.

`ssite COMMAND --help` displays parameters for COMMAND.

## Contributing

Contributions welcome. Fork and send a pull request to the [GitHub
repository](https://github.com/tswast/ssite).

* Linter: `flake8`
* Test harness: `pytest`

## License

Licensed under Apache License, Version 2.0. See
[LICENSE](https://github.com/tswast/ssite/blob/master/LICENSE).
