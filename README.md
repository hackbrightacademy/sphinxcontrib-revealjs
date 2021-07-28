# sphinxcontrib-revealjs

This is a work in progress.

## Configuration

### `revealjs_vertical_slides`

Enable/disable vertical slides. Defaults to `True`. Doesn't actually work right now.

### `revealjs_permalinks`

Enable permalinks. Defaults to False

### `revealjs_theme`

Override builder's default theme.

### `revealjs_theme_options`

- `revealjs_theme`: Revealjs theme (see Revealjs docs for list of themes)

## Automatic slide breaks

Headings 1&ndash;2 automatically create slide breaks

## Directives

- interslide
- newslide
- speaker
- incremental

## Development

Depend on Revealjs (git submodule). See https://git-scm.com/book/en/v2/Git-Tools-Submodules

##### Clone this repo w/ submodules

```
$ git clone --recurse-submodules <url for this repo>
```

##### Pull upstream changes

```
$ git submodule update --remote lib/revealjs
```