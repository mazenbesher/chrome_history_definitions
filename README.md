<!-- TOC -->

- [1. Functionality](#1-functionality)
- [2. To save results](#2-to-save-results)
- [3. TODO simple:](#3-todo-simple)
- [4. TODO hard:](#4-todo-hard)

<!-- /TOC -->

# 1. Functionality
This script extracts the words after any define search query (see the regex `def_re`) from chrome history

# 2. To save results
Change `OUTPUT_*` options.

# 3. TODO simple: 
1. [x] add definitions to exports (through the option `ADD_DEFINITIONS` with get calls to `api.pearson.com`)
1. [x] spell check (done with pyenchant, controlled with the option `SPELL_CHECK `)
1. [x] trim words (option `TRIM`)
1. [x] sort according to search date (done through using lists instead of sets)
1. [x] remove duplicates (using `more_itertools.unique_everseen`)
1. [ ] arg params for option toggles and constants
1. [ ] add help for CLI

# 4. TODO hard:
1. [ ] csv exprot with selected headers (definition, synonyms, ... other fields from API)
1. [ ] quiz mode (e.x. given the definition choose the word)
