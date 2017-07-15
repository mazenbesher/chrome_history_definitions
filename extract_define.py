#!/usr/bin/python3
import sqlite3
import re
import shutil
import tempfile
import os
import json
import argparse
import atexit

# parse arguments (btw all are optional)
parser = argparse.ArgumentParser()

# options
parser.add_argument("-t","--trim", help="trim words from spaces, tabs and common delimiters such as \"", action="store_true")
parser.add_argument("-sp","--spell-check", help="check if words are spelled correctly (requires pyenchant)", action="store_true")
parser.add_argument("-as","--accept-sentences", help="accept entries if history consisting from multiple words", action="store_true")
parser.add_argument("-np","--no-duplicates", help="remove duplicates", action="store_true")
parser.add_argument("-s","--stats", help="print status at the end of execution", action="store_true")
parser.add_argument("-ad","--add-definitions", help="request for definitions as json and save them in OUTPUT_DEF_JSON", action="store_true")
parser.add_argument("-alpha","--alpha-sorted", help="sort result alphabetically (default chronological order)", action="store_true")

# constants
parser.add_argument("--user", help="User name for DB_PATH", type=str, required=False, default=r"Mazen")
parser.add_argument("-db", "--db-path", help="path of the history file (the database)", type=str, required=False, default=None)
parser.add_argument("-l", "--limit", help="limit number of words", type=int, required=False, default=9999)
parser.add_argument("-cf", "--cache-file", help="cache file path", type=str, required=False, default=r"cache")
parser.add_argument("-csv","--csv-export", help="export words to csv field with different fields (require --add-definitions)", type=str, required=False, default=r"sample/export.csv")

args = parser.parse_args()

# constants
USER_NAME       = args.user  # no need if DB_PATH is provided                  
DICT_GET        = r"http://api.pearson.com/v2/dictionaries/ldoce5/entries?headword=" # with json response
OUTPUT_DEF_JSON = r"sample/definitions.json"  # for definitions
OUTPUT_WORDS    = r"sample/words.txt"
CACHE_FILE      = args.cache_file
WORD_LIMIT      = args.limit
DB_PATH         = args.db_path
CSV_EXPORT      = args.csv_export

# options
TRIM                = args.trim 
ACCEPT_SENTENCES    = args.accept_sentences
SPELL_CHECK         = args.spell_check
NO_DUPLICATES       = args.no_duplicates
ADD_DEFINITIONS     = args.add_definitions
PRINT_STATS         = args.stats
ALPH_SORTED         = args.alpha_sorted  # else sorted by search-date (newest first / chronological order)

# stats
STATS_API_CALLS      = 0
STATS_TOTAL_WORDS    = 0
STATS_FILTERED_WORDS = 0
STATS_FROM_CACHE     = 0
STATS_DUPLICATES     = 0

# check options conflicts
if ADD_DEFINITIONS and ACCEPT_SENTENCES:
    exit("Can't add definitions for sentences")

if CSV_EXPORT != None and not ADD_DEFINITIONS:
    exit("Can't export to csv if not allowed to request for definitions")

# conditional imports
if SPELL_CHECK:
    import enchant

if NO_DUPLICATES:
    from more_itertools import unique_everseen

if ADD_DEFINITIONS:
    import urllib.request

# db path auto generating
if DB_PATH == None:
    if os.name == "posix":
        # Ubuntu sub-system
        DB_PATH = r"/mnt/c/Users/" + USER_NAME + \
            r"/AppData/Local/Google/Chrome/User Data/Default/History"
    elif os.name == "nt":
        # Windows
        DB_PATH = r"C:\Users\\" + USER_NAME + \
            r"\AppData\Local\Google\Chrome\User Data\Default\History"
    else:
        print("Propably OS is not supported (assuming unix)")
        print("Please provide chrome histroy path (DB_PATH), if this is not working!")
        DB_PATH = r"~/Library/Application Support/Google/Chrome/Default/History"

# check if history db exists
if not os.path.isfile(DB_PATH):
    exit("Can't find the history db in the provided DB_PATH")

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
STATS_TOTAL_WORDS = len(words)

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
    STATS_DUPLICATES = STATS_TOTAL_WORDS - len(words)


# filter words (TRIM, WORDS_LIMIT, SPELL_CHECK, ACCEPT_SENTENCES)
filtered_words = []
for word in words[:WORD_LIMIT]:  # WORDS_LIMIT
    # TRIM
    if TRIM:
        word = word.strip(" \t\n\r\"',.;")  # trim

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
STATS_FILTERED_WORDS = len(filtered_words)

# export
# txt
with open(OUTPUT_WORDS, 'w') as f:
    for word in filtered_words:
        f.write(word + '\n')
print("Saved words to " + OUTPUT_WORDS)

# cache_to_file for saving API requests
def cache_to_file(file_name):
    try:
        cache = json.load(open(file_name, 'r'))
    except (IOError, ValueError):
        cache = {}

    atexit.register(lambda: json.dump(cache, open(file_name, 'w')))

    def decorator(func):
        def new_func(param):
            global STATS_FROM_CACHE
            if param not in cache:
                cache[param] = func(param)
            else:
                STATS_FROM_CACHE += 1
            return cache[param]
        return new_func

    return decorator

# json (if ADD_DEFINITIONS)
@cache_to_file(CACHE_FILE)
def lookup(word):
    global STATS_API_CALLS
    assert len(word.split()) == 1  # just to be sure
    with urllib.request.urlopen(DICT_GET + word) as response:
        STATS_API_CALLS += 1
        if response.status == 200:
            data = json.loads(response.read().decode())
            if data['results']:  # else discard (assume wrong word)
                return data['results']
    return None

if ADD_DEFINITIONS:
    json_data = {}
    # add definition for single words (note: words without definitions will be discarded, assumed to be wrong)
    assert not ACCEPT_SENTENCES
    for word in filtered_words:
        definition = lookup(word)
        if definition != None:
            json_data[word] = definition

    with open(OUTPUT_DEF_JSON, 'w') as f:
        json.dump(json_data, f)

    print("Saved definitions to: " + OUTPUT_DEF_JSON)

# csv
if CSV_EXPORT != None:
    assert ADD_DEFINITIONS and len(json_data) > 0 # to be sure

    separator = ";"
    with open(CSV_EXPORT, 'w') as f:
        for word in filtered_words:
            for data in json_data.get(word, []):
                # special for `pearson` (headword ; definition ; pos ; example)
                senses = data.get('senses', [])
                if senses == None: continue
                for sense in senses:
                    for i, definition in enumerate(sense.get('definition', [])):
                        headword = data.get('headword', '')
                        pos = data.get('part_of_speech', '')

                        examples = sense.get('examples', [])
                        example = ""
                        if len(examples) > 0 and len(examples[i]) > 0:
                            example = examples[i]['text']

                        f.write(headword + separator + definition + separator + pos + separator + example + "\n")

    print("Saved csv to: " + CSV_EXPORT)

# print stats
if PRINT_STATS:
    print("Total words: " + str(STATS_TOTAL_WORDS))
    print("Filtered words (words remaining after filtering): " + str(STATS_FILTERED_WORDS))

    if NO_DUPLICATES:
        print("Duplicates: " + str(STATS_DUPLICATES))

    if ADD_DEFINITIONS:
        print("API calls: " + str(STATS_API_CALLS))
        print("Words from cache: " + str(STATS_FROM_CACHE))
