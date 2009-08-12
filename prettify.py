#!/usr/bin/python

# ingests messy html files and spits them back out sanitized.

from BeautifulSoup import BeautifulSoup

import os, sys, re

#try:
#    indir = sys.argv[1]
#except:
#    print 'usage: ./prettify.py path/to/files/ '
#    sys.exit()

challenge_files = ['C1-Challenge_11-fixed.htm']
indir = 'challenges/'
#challenge_files = os.listdir(indir)

for file in challenge_files:
    if file.find('pretty') >= 0:
        continue

    fp = open(indir+'/'+file)
    soup = BeautifulSoup(''.join(fp))
    saveas = indir + '/' + file.replace('.htm', '.pretty.htm') 
    print 'saving ' + saveas
    wp = open(saveas, 'w')
    wp.write(soup.prettify())

print '\nFinished!'
