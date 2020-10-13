from scholarly import scholarly
from scholarly import ProxyGenerator
import json

import logging
import threading
import time

pg = ProxyGenerator()
pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
scholarly.use_proxy(pg)
scholarly.set_retries(10)

keywords = [
    """ "DevOps" """, 
    """ "Software+Product+Lines" """,
    """ "Regulated+Domain" """,
    """ "FDA+Requirement" """,
    """ "Continuous+Delivery" """,
    """ "Continuous+Integration" """,
    """ "Automation+Systems" """,
    """ "Software+Validation" """,
    """ "Continuous+Software+Engineering" """
    ]

# Check number of articles for each keyword

executed_queries = []

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

print("Queries for initial keywords:")

def Count(search_query):
    count = 0
    for _ in search_query:
        count = count + 1
        # bib = e.__getattribute__("bib")
        # gsrank = bib['gsrank']

        # if int(gsrank) > 1000:
        #     break

        # PROBLEM: Google scholar will only return 100 pages with 10 items each (1000 items)

    return count

def CountQueryResultNumber(k, cMap):
    #search_query = scholarly.search_pubs(k)
    
    search_query = CreateSearchQuery(k)
    print(search_query._url)
    executed_queries.append(search_query._url)
    cMap[k] = Count(search_query)

countMap = dict()
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

'''
Tue 13 Oct 2020 12:28:14 AM CEST

DevOps 1000
Software Product Lines 980
Regulated Domain 1000
FDA Requirement 999
Continuous Delivery 980
Continuous Integration 980
Automation Systems 980
Software Validation 980
Continuous Software Engineering 980
'''

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

logging.info("Main    : wait for the thread to finish")
for t in threads:
    t.join()

print("Results for combined keywords", k)
for tup in combined_results:
    keyword = tup[0]
    combinedDict = tup[1]
    print("Rest combined with", keyword)
    for key in combinedDict:
        print(key, combinedDict[key])
        
'''

'''

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
