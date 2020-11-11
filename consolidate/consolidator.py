import io
from contextlib import redirect_stdout
import os
import sys
import boto3
import subprocess
from os import path
import time
import logging

def CaptureOutput(function, outputfilename, base_path):
    """Captures output from function, and saves it as a file. File gets uploaded to S3"""
    path = f"{base_path}{outputfilename}"
    f = io.StringIO()
    with redirect_stdout(f):
        function()
    out = f.getvalue()
    output = open(path, "w")
    output.write(out)
    output.flush()
    output.close()
    s3_resource.Object(AWS_BUCKET_NAME, path).upload_file(Filename=path)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    # remove empty lines
    cleaned_list = []
    for line in lst:
        if not line.strip() == "":
            cleaned_list.append(line.strip())

    for i in range(0, len(cleaned_list), n):
        yield cleaned_list[i:i + n]

def Consolidate(folderpath):
    """Populates articles_dict with information from results folder. Removes duplicates"""
    for directory, subdirectories, files in os.walk(folderpath):
        # if there are subdirectories, they have already been sorted
        if(subdirectories.__len__() > 0):
            # Process files from subdirectories
            for directory in subdirectories:
                Consolidate(os.path.join(base_path, directory))
        else:
            # Process unsorted files
            for file in files:
                filepath = os.path.join(directory, file)
                with open(filepath, 'r') as file_object:
                    lines = file_object.readlines()[2:]
                    grouped = chunks(lines, 7)
                    for lst in grouped:
                        search_term = lst[0].replace("Search term ", "")
                        title = lst[1].replace("Title ", "")
                        author = lst[2].replace("Author ", "")
                        venue = lst[3].replace("Venue ", "")
                        year = lst[4].replace("Year ", "")
                        abstract = lst[5].replace("Abstract ", "")
                        url = lst[6].replace("Url ", "")

                        if title not in article_dict:
                            article_dict[title] = (([search_term], author, venue, year, abstract, [url], 1))
                        else:
                            (search_terms, author, venue, year, abstract, urls, count) = article_dict[title]
                            search_terms.append(search_term)
                            if url not in urls:
                                urls.append(url)
                            article_dict[title] = ((search_terms, author, venue, year, abstract, urls, count + 1))

def create_csv_output():
    """Takes the article_dict without duplicates with the collected information from scholar"""
    article_counts = []
    for article in article_dict:
        article_counts.append((article, article_dict[article][6]))

    article_counts.sort(key=lambda tup: tup[1], reverse=True)

    csv_content = ""
    for t in article_counts:
        a = t[0]
        article_details = article_dict[a]
        csv_content = csv_content + f"{a.strip()}{CSV_DELIMITER}{article_details[0]}{CSV_DELIMITER}{article_details[1]}{CSV_DELIMITER}{article_details[2]}{CSV_DELIMITER}{article_details[3]}{CSV_DELIMITER}{article_details[4]}{CSV_DELIMITER}{article_details[5]}{CSV_DELIMITER}{article_details[6]}\n"

    csv = f"""title{CSV_DELIMITER}search_terms_list{CSV_DELIMITER}author{CSV_DELIMITER}venue{CSV_DELIMITER}year{CSV_DELIMITER}abstract{CSV_DELIMITER}url_list{CSV_DELIMITER}count\n{csv_content.strip()}""".strip()
    print(csv)

def print_article_overview():
    """Prints the results from Consolidate() into consolidate.txt"""
    article_counts = []
    for article in article_dict:
        article_counts.append((article, article_dict[article][6]))

    article_counts.sort(key=lambda tup: tup[1], reverse=True)

    for t in article_counts:
        a = t[0]
        c = t[1]

        print(a, f"(count {c})")
        print(article_dict[a][0])
        print()

def syncs3():
    """Draft function for syncing S3 bucket before consolidating"""
    subprocess.run(["./sync_s3.sh", "/dev/null"], capture_output=True)




article_dict = dict()
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
FILE = os.getenv('FILE')
inputfilename = FILE.split('/')[1].split('.')[0]
base_path = f"output/{inputfilename}/articles/"
CSV_DELIMITER = 'Æ'
s3_resource = boto3.resource(
    's3',
    aws_access_key_id= os.getenv("AWS_KEY_ID"),
    aws_secret_access_key= os.getenv("AWS_SECRET"))

logging.basicConfig(level=logging.DEBUG)

def main():
    logging.debug("Starting consolidate")
    consolidated = False
    while not consolidated:
        if os.path.exists(base_path) and os.path.exists(f"output/{inputfilename}/lvl3.txt"): 
            Consolidate(base_path) # populates article_dict()

            outputfilename = "consolidated.txt"
            CaptureOutput(print_article_overview, outputfilename, base_path)

            outputfilename = f"{inputfilename}_consolidated.csv"
            CaptureOutput(create_csv_output, outputfilename, base_path)
            consolidated = True

        else: 
            logging.info("Sleeping for 5 min before sync") 
            time.sleep(300) # 5 min
            # syncs3()
            
    exit(0)

main()