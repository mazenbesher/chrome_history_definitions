<!-- TOC -->

- [1. Functionality](#1-functionality)
- [2. To save results](#2-to-save-results)
- [3. Options](#3-options)
- [4. TODOs](#4-todos)

<!-- /TOC -->

# 1. Functionality
This script extracts the words after any define search query (see the regex `def_re`) from chrome history.  
Then you can save those words, trim them, remove duplicates and even look up for their definitions (see [Options](#3-options))

# 2. To save results
Change `OUTPUT_*` options.  

# 3. Options
```
usage: extract_define.py [-h] [-t] [-sp] [-as] [-np] [-s] [-ad] [-alpha]
                         [--user USER] [-db DB_PATH] [-l LIMIT]
                         [-cf CACHE_FILE] [-csv CSV_EXPORT]

optional arguments:
  -h, --help            show this help message and exit
  -t, --trim            trim words from spaces, tabs and common delimiters
                        such as "
  -sp, --spell-check    check if words are spelled correctly (requires
                        pyenchant)
  -as, --accept-sent    accept entries if history consisting from multiple
                        words
  -np, --no-duplicates  remove duplicates
  -s, --stats           print status at the end of execution
  -ad, --add-def        request for definitions as json and save them in
                        OUTPUT_DEF_JSON
  -alpha, --alpha-sort  sort result alphabetically (default chronological
                        order)
  --user USER           User name for DB_PATH
  -db DB_PATH, --db-path DB_PATH
                        path of the history file (the database)
  -l LIMIT, --limit LIMIT
                        limit number of words
  -cf CACHE_FILE, --cache-file CACHE_FILE
                        cache file path
  -csv CSV_EXPORT, --csv-export CSV_EXPORT
                        export words to csv field with different fields
                        (requires --add-definitions)
```

Recommended options:
```
> python3 extract_define.py --trim --spell-check --no-duplicates --stats
```

# 4. TODOs
1. [x] add definitions to exports (through the option `ADD_DEFINITIONS` with get calls to `api.pearson.com`)
1. [x] spell check (done with pyenchant, controlled with the option `SPELL_CHECK`)
1. [x] trim words (option `TRIM`)
1. [x] sort according to search date (done through using lists instead of sets)
1. [x] remove duplicates (using `more_itertools.unique_everseen`)
1. [x] arg parser for option toggles and 
1. [ ] arg parser for option constants (not all yet)
1. [x] add help for CLI
1. [x] cache calls for definitions (using decorators and json dump)
1. [ ] right now `OUTPUT_DEF_JSON == CACHE_FILE` since two are the same json dumps, add options for formating `OUTPUT_DEF_JSON`
1. [ ] separated file for meta data (such as args options/help)
1. [ ] regex to match any word after `def*`
1. [ ] binary distributions (continuous integration, see [pyinstaller](http://www.pyinstaller.org/))
1. [x] csv export
1. [ ] make csv (and the separator) fields customizable
1. [ ] quiz mode (e.x. given the definition choose the word)
1. [ ] CLI quiz mode
1. [ ] progress bar while fetching words from API (see [tqdm](https://pypi.python.org/pypi/tqdm))
1. [ ] export as anki-compatible format with the option to export different fields (such as definition, synonym, etc)