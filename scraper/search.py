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
import time 
import boto3


# This script takes 1 argument
#   Argument 1: keywordlist path


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


def ExecuteLvl2KeywordCombinations(keywords):
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

    print("Results for combined keywords")
    for tup in combined_results:
        keyword = tup[0]
        combinedDict = tup[1]
        print("keywords combined with", keyword)
        for key in combinedDict:
            print("    ", key, combinedDict[key])

    return (threads, combined_results)


def ExecuteLvl3KeywordCombinations(keywords):
    threads = []
    known_searches = []
    results = []

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
                        # above if statements ensure values not euqal and not repeat

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

        results.append((k1, keyword_combination_results))
    
    return (threads, results)

# fetch title and abstract information threaded
def PrintResultsAndCreateThreadsForSelectedQueries(input_results):
    results = []
    threads = []
    print()
    print("Results for combined keywords")
    print()
    for tup in input_results:
        keyword = tup[0]
        combinedDict = tup[1]
        print("    ", "Combinations with", keyword.strip())
        for key in combinedDict:
            num = combinedDict[key]
            print('        ', key, num)
            if num < THRESHOLD:
                logging.info("Main    : before creating thread")
                t = threading.Thread(target=RetrieveTitleAndAbstract, args=(key, results), daemon=False)
                logging.info("Main    : before running thread")
                t.start()
                threads.append(t)
        print()
    return (threads, results)

# Convert list(results) to dict(results_dict)
def ConvertListToDict(results):
    results_dict = dict()
    for e in results:
        (key, title, author, venue, year, abstract, url) = e

        # initialize list before adding elements if first time we see key
        if not key in results_dict:
            results_dict[key] = []

        results_dict[key].append((title, author, venue, year, abstract, url))
    return results_dict

def PutArticleInformationInBucket(results_dict):
    # Print selected articles information. Captures output and prints as file, and throws file in s3 bucket
    print()
    for key in results_dict:
        outputPath = BASE_PATH+"articles"+'/'
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        f = io.StringIO()
        with redirect_stdout(f):
            print("Showing papers for search query", key)
            for v in results_dict[key]:
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


# Check number of articles for each combination of keywords
# Multithreaded
def CombinedSearchLevelTwo():
    (threads, results) = ExecuteLvl2KeywordCombinations(keywords)
    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()

    (threads, results) = PrintResultsAndCreateThreadsForSelectedQueries(results)
    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()

    PutArticleInformationInBucket(ConvertListToDict(results))

# Check number of articles for combinations of three keywords
# Multithreaded
def CombinedSearchLevelThree():    
    (threads, results) = ExecuteLvl3KeywordCombinations(keywords)
    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()

    (threads, results) = PrintResultsAndCreateThreadsForSelectedQueries(results)
    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()

    PutArticleInformationInBucket(ConvertListToDict(results))

def ExtractKeywords():
    # load keywords from file
    keywordlistfile = open(FILE, "r")
    keywords = []
    for l in keywordlistfile:
        keywords.append(f""" "{l.replace(' ', '+').strip()}" """)
    keywordlistfile.close()
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
    return keywords

def CreateBucketIfDoesntExists():
    # create s3 bucket if it doesnt exist
    try: 
        s3_resource.create_bucket(Bucket=AWS_BUCKET_NAME,
                                CreateBucketConfiguration={
                                    f'LocationConstraint': '{AWS_REGION}'})
    except:
        print("Bucket already exists")

def CreateOutputDirectories():
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

def CaptureOutputAsFileAndUpload(function, outputfilename, BASE_PATH):
    path = f"{BASE_PATH}{outputfilename}"
    f = io.StringIO()
    with redirect_stdout(f):
        function()
    out = f.getvalue()
    output = open(path, "w")
    output.write(out)
    output.flush()
    output.close()
    s3_resource.Object(AWS_BUCKET_NAME, path).upload_file(
        Filename=path)

def sendTimingsEmail(end_one, end_two, end_three, BASE_PATH):
    import smtplib, ssl
    bucket_url = "https://%s.s3-%s.amazonaws.com/%s/" % (AWS_BUCKET_NAME, AWS_REGION, BASE_PATH)
    
    # timeings
    analysis_one = end_one - start
    analysis_two = end_two - end_one
    analysis_three = end_three - end_two
    analysis_entire = end_three - start

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
    """.format(inputfilename, int(analysis_one/60), int(analysis_two/60), int(analysis_three/60), int(analysis_entire/60), bucket_url)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


# Program Flow

## VARIABLES
executed_queries = []
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')
FILE = os.getenv('FILE')
inputfilename = FILE.split('/')[1].split('.')[0]
BASE_PATH = f"output/{inputfilename}"

s3_resource = boto3.resource(
    's3',
    aws_access_key_id= os.getenv("AWS_KEY_ID"),
    aws_secret_access_key= os.getenv("AWS_SECRET"))

# Setup Scholarly to crawl Scholar with Tor Proxy
pg = ProxyGenerator()
pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
scholarly.use_proxy(pg)
scholarly.set_retries(1000)

## MAIN

keywords = ExtractKeywords()
CreateOutputDirectories()
CreateBucketIfDoesntExists()

THRESHOLD = 50

# lvl 1 search
start = time.time()
# CaptureOutputAsFileAndUpload(InitialSearch, "lvl1.txt", BASE_PATH)
end_one = time.time()

# lvl 2 search
CaptureOutputAsFileAndUpload(CombinedSearchLevelTwo, "lvl2.txt", BASE_PATH)
end_two = time.time()

# lvl 3 search
CaptureOutputAsFileAndUpload(CombinedSearchLevelThree, "lvl3.txt", BASE_PATH)
end_three = time.time()

# Send report
sendTimingsEmail(end_one, end_two, end_three, BASE_PATH)

## END
