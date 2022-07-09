# sphinxcontrib-revealjs

This is a work in progress.

- [Features](#features)
  - [Use the same `*.rst` file to generate slides](#use-the-same-rst-file-to-generate-slides)
  - [Sections automatically create slide breaks](#sections-automatically-create-slide-breaks)
  - [Manually add slide breaks](#manually-add-slide-breaks)
  - [Animate content with RevealJS `fragment`](#animate-content-with-revealjs-fragment)
  - [Speaker notes](#speaker-notes)
- [Configuration](#configuration)
  - [`revealjs_theme`](#revealjs_theme)
  - [`revealjs_theme_options["revealjs_theme"]`](#revealjs_theme_optionsrevealjs_theme)
  - [`revealjs_break_on_transition`](#revealjs_break_on_transition)
  - [`revealjs_newslides_inherit_titles`](#revealjs_newslides_inherit_titles)
- [Directives](#directives)
- [Development](#development)

## Features

### Use the same `*.rst` file to generate slides

It's amazing!

### Sections automatically create slide breaks

Sections level 1&ndash;3 automatically create slide breaks.

There's no way to override this behavior (but we're working on it!).

### Manually add slide breaks

Add a Sphinx transition (`---`) to break a slide:

```rst
Slide one

---

Slide two!
```

You can also disable this feature and use the `.. newslide::` directive instead:

```rst
Slide one

.. newslide::

Slide two!
```

### Animate content with RevealJS `fragment`

Make list items appear one at a time:

```rst
.. incr:: nest

   - Appears first
     - Appears second
   - Appears third
```

If you want nested items to appear at the same time as their parent, use `item`:

```rst
.. incr:: item

   - Appears first
     - Appears first too
   - Appears second
```

Or make entire paragraphs appear one at a time:

```rst
Initial contents of the slide.

.. incr:: one

   Then this paragraph and image will appear!

   .. image:: hello.png
```

### Speaker notes

Use `.. speaker::` to add speaker notes! During the presentation, press <kbd>s</kbd> to
open [RevealJS's speaker view](https://revealjs.com/speaker-view/).


## Configuration

### `revealjs_theme`

Name of the Sphinx theme to use.

This is **not** how you override the RevealJS theme. To do that, use
[`revealjs_theme_options`](#revealjs_theme_optionsrevealjs_theme) instead.

*Defaults to `"revealjs"`.*

### `revealjs_theme_options["revealjs_theme"]`

Use this to set the [RevealJS theme](https://revealjs.com/themes/).

*Defaults to `"black"`.*

### `revealjs_break_on_transition`

Set to `False`, if you don't want slides to break on transitions (`---`).

*Defaults to `True`.*

### `revealjs_newslides_inherit_titles`

By default, the `.. newslide::` directive will copy the title of its parent section. If
you don't want that, set this to `False`.

*Defaults to `True`.*

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