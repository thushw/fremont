#!/usr/bin/python
import requests
import datetime
import os
from bs4 import BeautifulSoup
import re
from sets import Set

bike_dirs = {"east": "north", "west": "south"}

#get bike status for yesterday
def bike_count(direction):
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday.strftime("%Y%m%d")
    dir_part = "102020981" if direction == "east" else "101020981"
    url = "http://www.eco-public.com/api/cw6Xk4jW4X4R/data/periode/%s/?begin=%s&end=%s&step=4" % (dir_part, yesterday.strftime("%Y%m%d"), today.strftime("%Y%m%d"))
    r = requests.get(url)
    return r.json()[0]['comptage']

def number_and_phrase(match):
    return (int(match.group(1)), match.group(2)) if match is not None else ()

def download_integers():
    r = requests.get("http://www2.stetson.edu/~efriedma/numbers.html")
    html = r.text
    #split the page into html lines, taking care to handle line ends.
    #then get just the interesting integers, which seems to have a distint font size=+3
    entries = filter(lambda entry: re.search(r"<font size=\+3 ", entry), re.split("<br>[\r\n\s]*", html))
    #apply the html parser to each line to extract just the text
    number_lines = map(lambda entry: BeautifulSoup(entry, 'html.parser').get_text(), entries)
    #one more reg exp for each text line to get the integer with the corresponding phrase
    numbers_list = filter(lambda tuple: True if tuple else False, map(lambda line: number_and_phrase(re.search(r"(\d+)(.+)", line)), number_lines))

    #store integer: phrase in a dictionary
    hash = dict(numbers_list)
    #some sanity test -> it is a web page, may change
    if not test(html, hash):
        print ("WARN: not a perfect screen scrape...")
    return hash

#form cute tweet message
def message(east_count, west_count, quote=None):
    formatted_total = "{:,}".format(east_count+west_count)
    m = "%s bikes rode across the fremont bridge yesterday. (%s %s)" % (formatted_total, formatted_total, quote) if quote \
        else "%s bikes rode across the fremont bridge yesterday." % formatted_total
    return m[:140]

#tweet it
def tweet(msg):
    os.system("twurl -d 'status=%s' /1.1/statuses/update.json" % msg)

easterners = int(bike_count("east"))
westerners = int(bike_count("west"))

def test(html, hash):
    #extract all interesting integers without the phrase; this is a simpler html parse and likely to get us all the integers
    #then see if all these integers and corresponding phrases were also extracted, using the more complex parse method
    soup = BeautifulSoup(html, "html.parser")
    missing = filter(lambda t: hash.get(t, '') == '', [int(e.get_text()) for e in soup.find_all('font', size='+3')])
    if missing:
        print (missing)
    return len(missing) == 0

phrase_hash = download_integers()

# s = Set([3358, 3360, 3342, 3375, 3318, 3499, 3501])

# for k in reversed(sorted(phrase_hash.keys())):
#     if k in s:
#         print ("%d => %s" % (k, phrase_hash[k]))

#tweet (message(easterners, westerners, phrase_hash[easterners+westerners]))

print (phrase_hash[7253])
