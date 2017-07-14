#!/usr/bin/python3
import sqlite3
import re
import shutil
import tempfile
import os

# constants
USER_NAME       = r"Mazen"
DICT_GET        = r"http://api.pearson.com/v2/dictionaries/ldoce5/entries?headword=" # with json response
OUTPUT_DEF_JSON = r"sample/definitions.json"  # for definitions
OUTPUT_WORDS    = r"sample/words.txt"
WORD_LIMIT      = 9999

# options
TRIM                = True
ACCEPT_SENTENCES    = False
SPELL_CHECK         = True
NO_DUPLICATES       = True
ADD_DEFINITIONS     = False
ALPH_SORTED         = False  # else sorted by search-date (newest first / chronological order)

# check options conflicts
if ADD_DEFINITIONS and ACCEPT_SENTENCES:
    exit("Can't add definitions for sentences")

# conditional imports
if SPELL_CHECK:
    import enchant

if NO_DUPLICATES:
    from more_itertools import unique_everseen

if ADD_DEFINITIONS:
    import urllib.request
    import json



# db path
if os.name == "posix":
    # Ubuntu sub-system
    DB_PATH = r"/mnt/c/Users/" + USER_NAME + \
        r"/AppData/Local/Google/Chrome/User Data/Default/History"
elif os.name == "nt":
    DB_PATH = r"C:\Users\\" + USER_NAME + \
        r"\AppData\Local\Google\Chrome\User Data\Default\History"
else:
    print("Propably OS is not supported (assuming unix)")
    DB_PATH = r"/mnt/c/Users/" + USER_NAME + \
        r"/AppData/Local/Google/Chrome/User Data/Default/History"

# copy history and delete it afterwards to avoid db locked error
temp_dir = tempfile.mkdtemp()
temp_db = shutil.copy(DB_PATH, temp_dir)

# sqlite
conn = sqlite3.connect(temp_db)
c = conn.cursor()

# regex
def_re = re.compile("(define|def)\s(.+?)(?=-)")
# second group includes the searched word (note group 0 is everthing matched)
target_group_index = 2
# Example title to be matched: define as late as - Google Search
# match any character until - if found
# (.+?) -> un-greedy search
# (?=-) until the dash - is found
# see: https://stackoverflow.com/questions/7124778/how-to-match-anything-up-until-this-sequence-of-characters-in-a-regular-expres

# fetch
words = []
for row in c.execute("SELECT title FROM urls ORDER BY last_visit_time DESC"):
    title = row[0]
    mat = def_re.match(title)
    if mat:
        word = mat.group(target_group_index)
        words.append(word)

# clean up
conn.close()
shutil.rmtree(temp_dir)

# set up spell checker
if SPELL_CHECK:
    d = enchant.Dict("en_GB")

# sort if needed
words = sorted(words) if ALPH_SORTED else words

# remove duplicates (while preserving order)
if NO_DUPLICATES:
    words = list(unique_everseen(words))

# filter words (TRIM, WORDS_LIMIT, SPELL_CHECK, ACCEPT_SENTENCES)
filtered_words = []
for word in words[:WORD_LIMIT]: # WORDS_LIMIT
    # TRIM
    if TRIM:
        word = word.strip(" \t\n\r\"")  # trim

    # ACCEPT_SENTENCES
    if not ACCEPT_SENTENCES:
        if len(word.split()) != 1:
            continue

    # SPELL_CHECK
    if SPELL_CHECK:
        word = " ".join([w for w in word.split() if d.check(w)])
        if len(word.strip()) == 0:
            continue

    filtered_words.append(word)
        
## export
# txt  
with open(OUTPUT_WORDS, 'w') as f:
    for word in filtered_words:
        f.write(word + '\n')
print("Saved words to " + OUTPUT_WORDS)

# json (if ADD_DEFINITIONS)
json_data = {}
if ADD_DEFINITIONS:
    # add definition for single words (note: words without definitions will be discarded, assumed to be wrong)
    assert not ACCEPT_SENTENCES
    for word in filtered_words:
        assert len(word.split()) == 1 # just to be sure
        with urllib.request.urlopen(DICT_GET + word) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                if data['results']:  # else discard (assume wrong word)
                    json_data[word] = data['results']

    with open(OUTPUT_DEF_JSON, 'w') as f:
        json.dump(json_data, f)

    print("Saved definitions to: " + OUTPUT_DEF_JSON)