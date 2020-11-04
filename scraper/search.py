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

# This script takes 1 argument
#   Argument 1: keywordlist path

# load keywords from file
keywordlist = open(os.getenv('FILE'), "r")

keywords = []
for l in keywordlist:
    keywords.append(f""" "{l.replace(' ', '+').strip()}" """)
keywordlist.close()
# example of resulting collection (from initial.txt)
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

# Setup Scholarly to crawl Scholar with Tor Proxy
pg = ProxyGenerator()
pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
scholarly.use_proxy(pg)
scholarly.set_retries(1000)

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
        url = pub.bib['url']
        abstract = "[Not Found]"
        if "abstract" in pub.bib:
            abstract = pub.bib['abstract']

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

# Check number of articles for each combination of keywords
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

# Check number of articles for combinations of three keywords
# Multithreaded
def CombinedSearchLevelThree():
    threads = []
    known_searches = []
    combined_results = []

    print("Executed Queries:")
    print()

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
    print()
    print("Results for combined keywords")
    print()
    for tup in combined_results:
        keyword = tup[0]
        combinedDict = tup[1]
        print("    ", "Combinations with", keyword.strip())
        for key in combinedDict:
            num = combinedDict[key]
            print('        ', key, num)
            if num < 10:
                logging.info("Main    : before creating thread")
                t = threading.Thread(target=RetrieveTitleAndAbstract, args=(key, results), daemon=False)
                logging.info("Main    : before running thread")
                t.start()
                threads.append(t)
        print()

    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()
        
    combination_results = dict()
    for e in results:
        (key, title, author, venue, year, abstract, url) = e

        # initialize list before adding elements if first time we see key
        if not key in combination_results:
            combination_results[key] = []

        combination_results[key].append((title, author, venue, year, abstract, url))

    # Maybe pipe out to individual files

    print()
    for key in combination_results:
        outputPath = base_path+"articles"+'/'
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        f = io.StringIO()
        with redirect_stdout(f):
            print("Showing papers for search query", key)
            for v in combination_results[key]:
                (title, author, venue, year, abstract, url) = v
                print()
                print("    ", "Search term", key)
                print("    ", "Title", title)
                print("    ", "Author", author)
                print("    ", "Venue", venue)
                print("    ", "Year", year)
                print("    ", "Abstract", abstract)
                print("    ", "Url", url)
                print()

        out = f.getvalue()
        output = open(outputPath+key+".out", "w")
        output.write(out)
        output.flush()
        output.close()

        s3_resource.Object(AWS_BUCKET_NAME, outputPath+key+".out").upload_file(
            Filename=outputPath+key+".out")

# Program Flow
import time 

start = time.time()

import boto3
s3_resource = boto3.resource(
    's3',
    aws_access_key_id= os.getenv("AWS_KEY_ID"),
    aws_secret_access_key= os.getenv("AWS_SECRET"))

AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')

try: 
    s3_resource.create_bucket(Bucket=AWS_BUCKET_NAME,
                            CreateBucketConfiguration={
                                'LocationConstraint': 'eu-west-1'})
except:
    print("Bucket already exists")

# Take output writtin to stdout during function call and pipe to file
FILE = os.getenv('FILE')
inputfilename = FILE.split('/')[1].split('.')[0]
base_path = f"output/{inputfilename}/"
if not os.path.exists(base_path):
    os.makedirs(base_path)

# # lvl 1
outputfilename = "lvl1.txt"
path = f"{base_path}{outputfilename}"
f = io.StringIO()
with redirect_stdout(f):
    InitialSearch()
out = f.getvalue()
output = open(path, "w")
output.write(out)
output.flush()
output.close()
s3_resource.Object(AWS_BUCKET_NAME, path).upload_file(
    Filename=path)

end_one = time.time()

# lvl 2
outputfilename = "lvl2.txt"
path = f"{base_path}{outputfilename}"
f = io.StringIO()
with redirect_stdout(f):
    CombinedSearchLevelTwo()
out = f.getvalue()
output = open(path, "w")
output.write(out)
output.flush()
output.close()
s3_resource.Object(AWS_BUCKET_NAME, path).upload_file(
    Filename=path)

end_two = time.time()

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
s3_resource.Object(AWS_BUCKET_NAME, path).upload_file(
    Filename=path)

end_three = time.time()

bucket_url = "https://%s.s3-%s.amazonaws.com/%s/" % (AWS_BUCKET_NAME, AWS_REGION, path)

# timeings
analysis_one = end_one - start
analysis_two = end_two - end_one
analysis_three = end_three - end_two
analysis_entire = end_three - start

import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = os.getenv("GMAIL")  # Enter your address
receiver_email = os.getenv("GMAIL")  # Enter receiver address
password = os.getenv("GMAIL_PASS")
message = """\
Subject: Processing of inputfile "{}" is now done.

This message is sent from Python. \n
\n
Level one analysis took {}m\n
Level two analysis took {}m\n
Level three analysis took {}m\n
\n
Elapsed analysis time {}m\n
\n
The result can be found in {}.\n
Please clean up the cloud resources.\n
""".format(inputfilename, int(analysis_one/60), int(analysis_two/60), (analysis_three/60), (analysis_entire/60), bucket_url)

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)


# TEARDOWN INFRASTRUCTURE

import requests
time.sleep(300)
url = "91.100.23.100:8080"
res = requests.post(url)

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
