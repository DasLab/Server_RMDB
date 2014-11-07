import argparse
import os
from repository.helpers import upload_file

parser = argparse.ArgumentParser()

parser.add_argument('directory', type=str)
parser.add_argument('publication', type=str)
parser.add_argument('description', type=str)
parser.add_argument('authors', type=str)
parser.add_argument('type', type=str)
parser.add_argument('pubmed_id', type=str)

args = parser.parse_args()
print 'Starting file upload'
for d in os.listdir(args.directory):
    f = open(args.directory + '/' + d)
    print (f, args.publication, args.description, args.authors, args.type, args.pubmed_id)
    upload_file(f, args.publication, args.description, args.authors, args.type, args.pubmed_id)
