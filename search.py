from scholarly import scholarly
from scholarly import ProxyGenerator
import json

pg = ProxyGenerator()
pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
scholarly.use_proxy(pg)
scholarly.set_retries(3)

keywords = [
    'DevOps', 
    'Software Product Lines',
    'Embedded Devices', 
    'Regulated Domain',
    'FDA Requirements',
    'Continuous Delivery'
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

        if int(gsrank) > 10:
            break

    countMap[k] = count

for t in countMap:
    print(t, countMap[t])


'''
dda
'''

# Check combinations with fewest returns







#sq = next(search_query)
#print(next(search_query))

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


