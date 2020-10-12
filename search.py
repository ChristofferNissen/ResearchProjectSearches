from scholarly import scholarly
from scholarly import ProxyGenerator
import json

pg = ProxyGenerator()
pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
scholarly.use_proxy(pg)
scholarly.set_retries(10)

keywords = [
    'DevOps', 
    'Software Product Lines',
    'Regulated Domain',
    'FDA Requirement',
    'Continuous Delivery',
    'Continuous Integration',
    'Automation Systems',
    'Software Validation',
    'Continuous Software Engineering'
    ]

# Check number of articles for each keyword

countMap = dict()
for k in keywords:
    search_query = scholarly.search_pubs(k)
    
    count = 0
    for e in search_query:
        count = count + 1
        bib = e.__getattribute__("bib")
        gsrank = bib['gsrank']

        if int(gsrank) > 1000:
            break

    countMap[k] = count

print("Baseline count:")
for t in countMap:
    print(t, countMap[t])

'''

'''

# Check combinations with fewest returns

known_searches = []

for k in keywords:
    # for each keyword, try combining with rest of keywords

    keyword_combination_results = dict()
    for k2 in keywords:
        if not k == k2:
            search_string = k + ' ' + k2

            # avoid repeat combinations
            if not search_string in known_searches:
                known_searches.append(search_string)

                search_query = scholarly.search_pubs(search_string)

                count = 0
                for e in search_query:
                    count = count + 1

                keyword_combination_results[search_string] = count

    print("Results for", k)
    for res in keyword_combination_results:
        print(res, keyword_combination_results[res]) 





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


