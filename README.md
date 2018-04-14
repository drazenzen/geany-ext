# geany-ext

Geany extensions files (plugins, colorschemes, snippets, ...)


## remember.py

Python plugin to remember files folds and bookmarks state between sessions.

### Install

+ Install [Geany](https://www.geany.org/ "Geany")
+ Install [Geanypy plugin](http://codebrainz.github.io/geanypy/ "GeanyPy")
+ Copy `remember.py` to Geany config plugins directory (usually `$HOME/.config/geany/plugins`)

### Usage

- On **every** document open event, plugin will check if there is saved folds/bookmarks data for opened file.
- On **every** document save event, plugin will scan the file and save folds/bookmarks info.
- On unloading plugin or closing Geany, data will be saved (as pickle object) to `remember.pcl` file in Geany config plugins directory.
