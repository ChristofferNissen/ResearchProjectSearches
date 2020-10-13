from scholarly import scholarly
from scholarly import ProxyGenerator
import json

import logging
import threading
import time

pg = ProxyGenerator()
pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
scholarly.use_proxy(pg)
scholarly.set_retries(100)

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

def InitialSearch():
    print("Queries for initial keywords:")
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

# InitialSearch()
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

# CombinedSearchLevelTwo()
'''
Queries for initial keywords:
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Integration"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="FDA+Requirement"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="DevOps"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Software+Engineering"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Product+Lines"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Validation"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Delivery"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Regulated+Domain"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Automation+Systems"
Baseline count pr keyword:
 "DevOps"  1000
 "Continuous+Integration"  1000
 "Regulated+Domain"  998
 "Continuous+Software+Engineering"  999
 "Automation+Systems"  1000
 "FDA+Requirement"  997
 "Software+Product+Lines"  1000
 "Software+Validation"  998
 "Continuous+Delivery"  1000
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="FDA+Requirement"+"Continuous+Software+Engineering"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Delivery"+"Automation+Systems"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Validation"+"Continuous+Delivery"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Validation"+"Continuous+Integration"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Product+Lines"+"FDA+Requirement"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="DevOps"+"Automation+Systems"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="DevOps"+"Continuous+Software+Engineering"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Software+Engineering"+"Automation+Systems"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Integration"+"Regulated+Domain"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Integration"+"FDA+Requirement"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Product+Lines"+"Continuous+Software+Engineering"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Product+Lines"+"Continuous+Delivery"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Validation"+"Continuous+Software+Engineering"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Integration"+"Continuous+Delivery"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="DevOps"+"FDA+Requirement"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Automation+Systems"+"DevOps"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="FDA+Requirement"+"Software+Validation"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="FDA+Requirement"+"DevOps"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Regulated+Domain"+"Continuous+Delivery"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Delivery"+"Regulated+Domain"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Software+Engineering"+"DevOps"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="FDA+Requirement"+"Automation+Systems"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Delivery"+"Continuous+Integration"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="FDA+Requirement"+"Continuous+Integration"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Regulated+Domain"+"Continuous+Software+Engineering"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Automation+Systems"+"Continuous+Software+Engineering"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="DevOps"+"Regulated+Domain"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Automation+Systems"+"Software+Product+Lines"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Regulated+Domain"+"Automation+Systems"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Regulated+Domain"+"Software+Validation"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Software+Engineering"+"Continuous+Delivery"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Software+Engineering"+"Regulated+Domain"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Validation"+"Automation+Systems"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Delivery"+"Continuous+Software+Engineering"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Delivery"+"Software+Validation"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Delivery"+"DevOps"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Validation"+"DevOps"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Product+Lines"+"Regulated+Domain"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Delivery"+"FDA+Requirement"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Software+Engineering"+"Continuous+Integration"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Integration"+"Continuous+Software+Engineering"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Automation+Systems"+"Continuous+Delivery"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="DevOps"+"Software+Validation"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Automation+Systems"+"Regulated+Domain"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="FDA+Requirement"+"Regulated+Domain"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Validation"+"FDA+Requirement"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="FDA+Requirement"+"Software+Product+Lines"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="DevOps"+"Continuous+Delivery"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Regulated+Domain"+"Software+Product+Lines"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Automation+Systems"+"Continuous+Integration"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Integration"+"Automation+Systems"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Integration"+"Software+Validation"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="DevOps"+"Continuous+Integration"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Product+Lines"+"Software+Validation"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Validation"+"Regulated+Domain"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Product+Lines"+"Automation+Systems"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Regulated+Domain"+"FDA+Requirement"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="FDA+Requirement"+"Continuous+Delivery"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Software+Engineering"+"FDA+Requirement"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Regulated+Domain"+"DevOps"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Product+Lines"+"Continuous+Integration"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Automation+Systems"+"FDA+Requirement"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Regulated+Domain"+"Continuous+Integration"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Integration"+"Software+Product+Lines"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Validation"+"Software+Product+Lines"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="DevOps"+"Software+Product+Lines"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Software+Engineering"+"Software+Product+Lines"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Automation+Systems"+"Software+Validation"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Software+Product+Lines"+"DevOps"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Delivery"+"Software+Product+Lines"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Integration"+"DevOps"
/scholar?hl=en&lr=lang_en&as_vis=0&as_sdt=0,33&q="Continuous+Software+Engineering"+"Software+Validation"
Results for combined keywords  "Continuous+Software+Engineering"
Rest combined with  "DevOps"
"DevOps"+"FDA+Requirement" 0
"DevOps"+"Regulated+Domain" 8
"DevOps"+"Software+Validation" 104
"DevOps"+"Automation+Systems" 273
"DevOps"+"Software+Product+Lines" 303
"DevOps"+"Continuous+Software+Engineering" 497
"DevOps"+"Continuous+Delivery" 1000
"DevOps"+"Continuous+Integration" 999
Rest combined with  "Software+Product+Lines"
"Software+Product+Lines"+"FDA+Requirement" 0
"Software+Product+Lines"+"Regulated+Domain" 12
"Software+Product+Lines"+"Continuous+Software+Engineering" 100
"Software+Product+Lines"+"Software+Validation" 179
"Software+Product+Lines"+"Continuous+Delivery" 253
"Software+Product+Lines"+"DevOps" 303
"Software+Product+Lines"+"Automation+Systems" 424
"Software+Product+Lines"+"Continuous+Integration" 686
Rest combined with  "Regulated+Domain"
"Regulated+Domain"+"Continuous+Delivery" 7
"Regulated+Domain"+"Continuous+Software+Engineering" 2
"Regulated+Domain"+"Automation+Systems" 8
"Regulated+Domain"+"Software+Validation" 6
"Regulated+Domain"+"FDA+Requirement" 0
"Regulated+Domain"+"DevOps" 8
"Regulated+Domain"+"Software+Product+Lines" 12
"Regulated+Domain"+"Continuous+Integration" 16
Rest combined with  "FDA+Requirement"
"FDA+Requirement"+"Continuous+Software+Engineering" 0
"FDA+Requirement"+"DevOps" 0
"FDA+Requirement"+"Automation+Systems" 3
"FDA+Requirement"+"Continuous+Integration" 1
"FDA+Requirement"+"Regulated+Domain" 0
"FDA+Requirement"+"Software+Product+Lines" 0
"FDA+Requirement"+"Continuous+Delivery" 3
"FDA+Requirement"+"Software+Validation" 24
Rest combined with  "Continuous+Delivery"
"Continuous+Delivery"+"Regulated+Domain" 7
"Continuous+Delivery"+"FDA+Requirement" 3
"Continuous+Delivery"+"Software+Validation" 110
"Continuous+Delivery"+"Automation+Systems" 231
"Continuous+Delivery"+"Software+Product+Lines" 253
"Continuous+Delivery"+"Continuous+Software+Engineering" 512
"Continuous+Delivery"+"Continuous+Integration" 999
"Continuous+Delivery"+"DevOps" 1000
Rest combined with  "Continuous+Integration"
"Continuous+Integration"+"FDA+Requirement" 1
"Continuous+Integration"+"Regulated+Domain" 16
"Continuous+Integration"+"Software+Validation" 347
"Continuous+Integration"+"Automation+Systems" 462
"Continuous+Integration"+"Continuous+Software+Engineering" 589
"Continuous+Integration"+"Software+Product+Lines" 686
"Continuous+Integration"+"Continuous+Delivery" 999
"Continuous+Integration"+"DevOps" 999
Rest combined with  "Automation+Systems"
"Automation+Systems"+"Regulated+Domain" 8
"Automation+Systems"+"FDA+Requirement" 3
"Automation+Systems"+"Continuous+Software+Engineering" 18
"Automation+Systems"+"Continuous+Delivery" 231
"Automation+Systems"+"DevOps" 273
"Automation+Systems"+"Software+Validation" 249
"Automation+Systems"+"Software+Product+Lines" 424
"Automation+Systems"+"Continuous+Integration" 462
Rest combined with  "Software+Validation"
"Software+Validation"+"Regulated+Domain" 6
"Software+Validation"+"Continuous+Software+Engineering" 11
"Software+Validation"+"FDA+Requirement" 24
"Software+Validation"+"Continuous+Delivery" 110
"Software+Validation"+"DevOps" 104
"Software+Validation"+"Automation+Systems" 249
"Software+Validation"+"Software+Product+Lines" 179
"Software+Validation"+"Continuous+Integration" 347
Rest combined with  "Continuous+Software+Engineering"
"Continuous+Software+Engineering"+"Regulated+Domain" 2
"Continuous+Software+Engineering"+"FDA+Requirement" 0
"Continuous+Software+Engineering"+"Automation+Systems" 18
"Continuous+Software+Engineering"+"Software+Validation" 11
"Continuous+Software+Engineering"+"Software+Product+Lines" 100
"Continuous+Software+Engineering"+"DevOps" 497
"Continuous+Software+Engineering"+"Continuous+Delivery" 512
"Continuous+Software+Engineering"+"Continuous+Integration" 589
'''

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
                            t = threading.Thread(target=CountQueryResultNumber, args=(combined, keyword_combination_results), daemon=True)
                            logging.info("Main    : before running thread")
                            t.start()
                            threads.append(t)

        combined_results.append((k1, keyword_combination_results))

    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()

    print("Results for combined keyword pr keyword")
    for tup in combined_results:
        keyword = tup[0]
        combinedDict = tup[1]
        print("Combinations with", keyword)
        for key in combinedDict:
            print(key, combinedDict[key])
            
CombinedSearchLevelThree()
'''
see output.txt
'''

# Check combinations with low number to check if they match what we are looking for


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
