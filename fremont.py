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

#collect text for all siblings of this html section
#separate the text found in adjacent siblings from each other by a space
#and return this textual representation
#this is better than get_text() as this handles superscripts
def get_text_to_eol(font_section):
    text_parts = []
    section = font_section.next_sibling
    while section is not None:
        if section.name == 'a':
            text_parts.append(section.get_text())
        elif section.name is None:
            text_parts.append(unicode(section))
        else:
            if section.name == 'sup':
                text_parts.append('^')
            text_parts.append(section.get_text())
        section = section.next_sibling
    return ' '.join(text_parts)

def download_integers():
    r = requests.get("http://www2.stetson.edu/~efriedma/numbers.html")
    html = r.text

    #split the page into html lines, taking care to handle line ends.
    lines = re.split("<br>[\r\n\s]*", html)
    #then get just the interesting integers, which seems to have a distint font size=+3
    list_lines = list(filter(lambda x: x is not None, [re.search(r"<font size=\+3 .*", line) for line in lines]))
    #apply the html parser to each line
    soups = [BeautifulSoup(l.group(0), 'html.parser').font for l in list_lines]
    #get text for each line
    np_list = [(int(s.get_text()), get_text_to_eol(s)) for s in soups]
    hash = dict(np_list)
    #some sanity test -> it is a web page, may change
    if not test(html, hash):
        print ("WARN: not a perfect screen scrape...")
    return hash

#form cute tweet message
def message(east_count, west_count, quote=None):
    formatted_total = "{:,}".format(east_count+west_count)
    m = "%s bikes rode across the fremont bridge yesterday. (%s %s)" % (formatted_total, formatted_total, quote) if quote \
        else "%s bikes rode across the fremont bridge yesterday." % formatted_total
    #truncate to what is allowed by twitter
    return m[:140]

#tweet it
def tweet(msg):
    #make utf-8 strings in our output routine
    msg_utf8 = msg.encode('utf-8')
    print("tweeting %s" % msg_utf8)
    os.system("twurl -d 'status=%s' /1.1/statuses/update.json" % msg_utf8)

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

tweet (message(easterners, westerners, phrase_hash.get(easterners+westerners, None)))

#print (phrase_hash[7253])
