from scholarly import scholarly
from scholarly import ProxyGenerator
import json
import logging
import threading
import time
import sys
import io
from contextlib import redirect_stdout
import os

pg = ProxyGenerator()
pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
scholarly.use_proxy(pg)
scholarly.set_retries(100)

# This script takes 1 argument
#   Argument 1: keywordlist path

# load keywords from file
keywordlist = open(sys.argv[1], "r")

keywords = []
for l in keywordlist:
    keywords.append(f""" "{l.replace(' ', '+').strip()}" """)

keywordlist.close()

# example of resulting collection (initial.txt)
# keywords = [
#     """ "DevOps" """, 
#     """ "Software+Product+Lines" """,
#     """ "Regulated+Domain" """,
#     """ "FDA+Requirement" """,
#     """ "Continuous+Delivery" """,
#     """ "Continuous+Integration" """,
#     """ "Automation+Systems" """,
#     """ "Software+Validation" """,
#     """ "Continuous+Software+Engineering" """
#     ]

# Creates custom query and retrives the iterator from Scholarly
def CreateSearchQuery(keyword):
    # Parameters:
    #   hl: eng
    #   lang: eng
    #   as_vis: 0
    #   as_sdt: 0,33
    #   q: keyword
    query = f"""/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q={keyword.strip()}"""
    search_query = scholarly.search_pubs_custom_url(query)
    return search_query

# Traverses iterator from Scholarly to count number of articles
def Count(search_query):
    count = 0
    for _ in search_query:
        count = count + 1
        # bib = e.__getattribute__("bib") Probably the same as bib = e.bib...
        # gsrank = bib['gsrank']

        # if int(gsrank) > 1000:
        #     break

        # PROBLEM: Google scholar will only return 100 pages with 10 items each (1000 items)

    return count

# Thread workload. Count number of articles about keyword k
executed_queries = []
def CountQueryResultNumber(k, cMap):
    #search_query = scholarly.search_pubs(k)
    search_query = CreateSearchQuery(k)
    executed_queries.append(search_query._url)
    print(search_query._url)
    cMap[k] = Count(search_query)

def GetValuesFromBib(search_query, k, collection):
    for pub in search_query:
        title = pub.bib['title']
        author = pub.bib['author']
        venue = pub.bib['venue']
        year = pub.bib['year']
        #abstract = pub.bib['abstract']
        url = pub.bib['url']
        abstract = "[Not Found]"
        if "abstract" in pub.bib:
            abstract = pub.bib['abstract']

        # print("Title", title)
        # print("Author", author)
        # print("Venue", venue)
        # print("Year", year)
        # #print("Abstract", abstract)
        # print("Url", url)

        collection.append((k, title, author, venue, year, abstract, url))

def RetrieveTitleAndAbstract(k, collection):
    search_query = CreateSearchQuery(k)    
    GetValuesFromBib(search_query, k, collection)

# Check number of articles for each keyword seperately
# Multithreaded
def InitialSearch():
    print("Queries for initial keywords:")
    countMap = dict() # Python collections are threadsafe
    threads = []
    for k in keywords:
        logging.info("Main    : before creating thread")
        t = threading.Thread(target=CountQueryResultNumber, args=(k, countMap), daemon=True)
        logging.info("Main    : before running thread")
        t.start()
        threads.append(t)

    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()

    logging.info("Main    : all done")

    print("Baseline count pr keyword:")
    for t in countMap:
        print(t, countMap[t])

# Multithreaded
def CombinedSearchLevelTwo():
    threads = []
    known_searches = []
    combined_results = []
    # Check combinations with fewest returns
    for k in keywords:
        # for each keyword, try combining with rest of keywords

        keyword_combination_results = dict()
        for k2 in keywords:
            if not k == k2:
                combined = k.strip() + "+" + k2.strip()

                # avoid repeat combinations
                if not combined in known_searches:
                    known_searches.append(combined)

                    logging.info("Main    : before creating thread")
                    t = threading.Thread(target=CountQueryResultNumber, args=(combined, keyword_combination_results), daemon=True)
                    logging.info("Main    : before running thread")
                    t.start()
                    threads.append(t)

        combined_results.append((k, keyword_combination_results))

    logging.info("Main    : wait for the threads to finish")
    for t in threads:
        t.join()

    print("Results for combined keywords", k)
    for tup in combined_results:
        keyword = tup[0]
        combinedDict = tup[1]
        print("Rest combined with", keyword)
        for key in combinedDict:
            print(key, combinedDict[key])

# Multithreaded
def CombinedSearchLevelThree():
    threads = []
    known_searches = []
    combined_results = []
    # Check combinations with fewest returns
    for k1 in keywords:
        # for each keyword, try combining with rest of keywords
        keyword_combination_results = dict()
        for k2 in keywords:
            if not k1 == k2:
                for k3 in keywords:
                    if not k3 == k2 and not k3 == k1:
                        
                        # sort keywords to avoid repeats when comparing out of order in known combined search strings
                        keys = []
                        keys.append(k1.strip())
                        keys.append(k2.strip())
                        keys.append(k3.strip())
                        keys.sort()

                        combined = keys[0] + "+" + keys[1] + "+" + keys[2]

                        # avoid repeat combinations
                        if not combined in known_searches:
                            known_searches.append(combined)

                            logging.info("Main    : before creating thread")
                            t = threading.Thread(target=CountQueryResultNumber, args=(combined, keyword_combination_results), daemon=False)
                            logging.info("Main    : before running thread")
                            t.start()
                            threads.append(t)

        combined_results.append((k1, keyword_combination_results))

    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()

    results = []
    threads = []
    print("Results for combined keywords")
    for tup in combined_results:
        keyword = tup[0]
        combinedDict = tup[1]
        print("Combinations with", keyword.strip())
        for key in combinedDict:
            num = combinedDict[key]
            print(key, num)
            if num < 10:
                logging.info("Main    : before creating thread")
                t = threading.Thread(target=RetrieveTitleAndAbstract, args=(key, results), daemon=False)
                logging.info("Main    : before running thread")
                t.start()
                threads.append(t)

    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()
        
    combination_results = dict()
    for e in results:
        (k, title, author, venue, year, abstract, url) = e
        tmp = str(k)
        tmp = tmp.replace('"+"', ' ')
        tmp = tmp.replace('"', '')
        tmp = tmp.replace('+', ' ')
        tmp = tmp.replace(' ', '')
        print(k)
        print(tmp)

        combination_results[tmp].append((title, author, venue, year, abstract, url))

    for e in combination_results:
        for v in combination_results[e]:
            (title, author, venue, year, abstract, url) = v
            print()
            print("Search term", k)
            print("Title", title)
            print("Author", author)
            print("Venue", venue)
            print("Year", year)
            print("Abstract", abstract)
            print("Url", url)
            print()

# Program Flow

# Take output writtin to stdout during function call and pipe to file
inputfilename = sys.argv[1].split('/')[1].split('.')[0]
base_path = f"output/{inputfilename}/"
if not os.path.exists(base_path):
    os.makedirs(base_path)

# # lvl 1
# outputfilename = "lvl1.txt"
# path = f"{base_path}{outputfilename}"
# f = io.StringIO()
# with redirect_stdout(f):
#     InitialSearch()
# out = f.getvalue()
# output = open(path, "w")
# output.write(out)
# output.flush()
# output.close()

# # lvl 2
# outputfilename = "lvl2.txt"
# path = f"{base_path}{outputfilename}"
# f = io.StringIO()
# with redirect_stdout(f):
#     CombinedSearchLevelTwo()
# out = f.getvalue()
# output = open(path, "w")
# output.write(out)
# output.flush()
# output.close()

# lvl 3
outputfilename = "lvl3.txt"
path = f"{base_path}{outputfilename}"
f = io.StringIO()
with redirect_stdout(f):
    CombinedSearchLevelThree()
out = f.getvalue()
output = open(path, "w")
output.write(out)
output.flush()
output.close()


# Next step
# Check combinations with low number to check if they match what we are looking for



## stashed code from documentation if handy later

# Retrieve the author's data, fill-in, and print
# search_query = scholarly.search_author('Steven A Cholewiak')
# author = next(search_query).fill()
# print(author)

# # Print the titles of the author's publications
# print([pub.bib['title'] for pub in author.publications])

# # Take a closer look at the first publication
# pub = author.publications[0].fill()
# print(pub)

# # Which papers cited that publication?
# print([citation.bib['title'] for citation in pub.citedby])
