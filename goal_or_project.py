#!/usr/bin/python

# an interactive script to help you annotate each of the millenium
# subgoals as either a goal or a project. will save results to a file
# called goals_project_index.txt. this file will get overwritten each
# time the script is run if the previous copy is not moved to another
# location.

import os, sys, re 
from document import Document, DocumentDecoder

try:
    import json
except: 
    try: 
        import simplejson as json
    except: 
        print 'Error: no json module installed.'
        sys.exit()

try:
    indir = sys.argv[1]
except:
    print 'usage: ./goal_or_project.py path/to/json/files/ '
    sys.exit()

def print_and_save(type):
    print "Here's your decisions:"
    wp = open("goals_project_index.txt", 'w')
    for key, type in type.iteritems():
        output = key+':\t'+type+'\n'
        wp.write(output)
        print output

json_files = os.listdir(indir)

# type is a dictionary correlating subgoals to their type-- either
# project (P) or goal (G)
type = {}
for file in json_files:
    fp = open(indir+'/'+file)
    document = json.load(fp, cls=DocumentDecoder)
    for subgoal, contents in document.subgoals.iteritems():
        print "\n\n============================ %s ========================" % subgoal
        # fucking unicode
        print contents.encode('utf-8', 'ignore')
        while True:
            input = raw_input("\n\nIs %s a goal? (enter 'g') or a project? (enter 'p') > " % subgoal)
            if input == 'g' or input == 'p':
                type[subgoal] = input
                break
            elif input == 'q':
                print_and_save(type)
                sys.exit()
            else:
                print "You must enter either 'p' or 'g'. Please try again."

# if we actually made it to the end, print and save
print_and_save(type)
