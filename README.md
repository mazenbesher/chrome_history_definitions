<!-- TOC -->

- [1. Functionality](#1-functionality)
- [2. To save results](#2-to-save-results)
- [3. Options](#3-options)
- [4. TODO](#4-todo)
    - [simple:](#simple)
    - [hard:](#hard)

<!-- /TOC -->

# 1. Functionality
This script extracts the words after any define search query (see the regex `def_re`) from chrome history.  
Then you can save those words, trim them, remove duplicates and even look up for their definitions (see [Options](#3-options))

# 2. To save results
Change `OUTPUT_*` options.  

# 3. Options
TODO  
Recommended options:
```
> python3 extract_define.py --trim --spell-check --no-duplicates --stats
```

# 4. TODO 
## simple: 
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

## hard:
1. [x] csv export
1. [ ] make csv (and the separator) fields customizable
1. [ ] quiz mode (e.x. given the definition choose the word)
1. [ ] progress bar while fetching words from API
1. [ ] export as anki-compatible format with the option to export different fields (such as definition, synonym, etc)
