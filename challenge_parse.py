#!/usr/bin/python

#####################################################################
# Overview: parses html versions of the chapters from The State Of The
# Future Index and extracts the challenge name, all the subgoals, the
# challenge summary, the list of proposed actions, and the useful
# links.  All files were run through the beautiful soup pretty()
# function before being run through this script. 

# Note 1: that this does NOT strip the html formatting within each of
# the extracted sections. we may do this later. 

# Note 2: i had to put some hacks in chapter 12 for it to work. search
# for the word 'hack' in chapter 12 to see details. 
#####################################################################

import os, sys, re, simplejson as json
from document import Document, DocumentEncoder

try:
    indir = sys.argv[1]
except:
    print 'usage: ./challenge_parse.py path/to/challenges/ '
    sys.exit()

challenge_files = os.listdir(indir)

# regex's for finding various parts of the file with subtle
# differences.
subgoal = re.compile(r'.*<a href="#(?P<subgoal_name>_.+)">.*')
comments_section = re.compile(r'<a name="_(Additional_)?(Comments_[Ff]rom)(_Participants)?')
links_section = re.compile('''<a name="_[Uu]seful_[Ww]ebsites''')

###########################################################
# Helper Functions
###########################################################

def strip_html(s):
    ''' strip the html tags from string s. '''
    html = re.compile(r'<[^<]*?>')
    return re.sub(html,'', s)

def save(documents):
    ''' saves each document object in a list of documents as a json
    file, using the challenge name as the filename'''

    print '***************** SAVING TO JSON ***************'
    for document in documents:
        challenge_name = strip_html(document.challenge)
        challenge_name = re.sub(r' *\? *', ' ', challenge_name)
        challenge_name = re.sub(r' *\n *', ' ', challenge_name)
        challenge_name = challenge_name.strip(' \n\t')
        saveas  = "json/"+challenge_name+".json"
        print saveas
        wp = open (saveas, "w")
        json.dump(document, wp, cls=DocumentEncoder)        


###########################################################
# Document Processing
###########################################################

documents = []
for file in challenge_files:
    # only work with the prettified html files
    if file.find("pretty") < 0 or file.endswith('~'):
        continue

    # XXX this should really be an attribute of the document, but meh.
    state = {
        'in_title': False,
        'in_contents': False,
        'in_body': False,
        'in_summary': False,
        'in_subgoals': False,
        'in_goal': False,
        'actions': False,
        'links': False,
        'finished': False,
    }

    print '============================ %s =========================' %file
    fp = open(indir+'/'+file)
    document = Document()
    documents.append(document)
    for line in fp:

        # get the challenge (chapter) name
        if line.find("<h1>") >= 0:
            state['in_title'] = True

        elif state['in_title']:
            if line.find("</h1>") >= 0:
                state['in_title'] = False
            else:
                document.challenge += line

        # get the list of subgoals        
        elif not state['in_contents'] and line.find("#_General_Description") >= 0:
            print 'Found Table of Contents'
            state['in_contents'] = True

        elif state['in_contents']:
            match = subgoal.match(line.strip()) 
            if not match:
                continue
            else:
                # check if we reached the Regional Considerations
                # section; if so, we're done with the subgoals.
                if line.find("#_Regional_Considerations") >= 0:
                    state['in_contents'] = False 
                    state['in_body'] = True
                    print '%d subgoals were:' % (len(document.subgoals))
                    for goal in document.subgoals.keys():
                        print '\t'+goal
                else:
                    # else it's an honest to goodness subgoal:
                    # initialize it.
                    document.subgoals[match.group('subgoal_name')] = ''

        elif state['in_body']:
            if line.find('''<a name="_Short_Overview''') >= 0:
                print '\nGetting summary...'
                state['in_summary'] = True
            elif state['in_summary']:
                # some have name="_General_Description_1",
                # "_General_Description_2", etc.
                if line.find('''<a name="_General_Description''') < 0:
                    document.summary += line
                else:
                    state['in_summary'] = False
                    state['in_subgoals'] = True
                    print 'Got Challenge Summary\n'

            elif state['in_subgoals']:

                # check this line to see if we've reached the next
                # goal, and update the state if so. 
                for goal in document.subgoals.keys():
                    if '''<a name="'''+goal+'''">''' in line:
                        print '*** Extracting Goal: \t%s' % goal                        
                        state['in_goal'] = goal
                        continue

                # else see if we've reached the end of ALL the goals
                if line.find('''<a name="_Regional_Considerations">''') >= 0:
                    print 'Reached end of subgoals'
                    state['in_subgoals'] = False
                    state['in_goal'] = False
                    for goal, contents in document.subgoals.iteritems():
                        if contents.strip() == '':
                            print 'Warning: subgoal %s is empty' % goal

                # else if we're inside a goal, add this line to the
                # current goal
                elif state['in_goal']:
                    document.subgoals[state['in_goal']] += line

            elif line.find('''<a name="_Suggested_Actions''') >= 0: # and not line.find('Actions_to_Address') < 0:
                print 'Entering state: actions'
                print line
                state['actions'] = True

            elif state['actions']:
                # as long as we dont hit the next section, add the line
                match = comments_section.match(line.strip()) 
                if match:
                    state['actions'] = False
                    if len(document.actions) > 0:
                        print '\nExtracted Actions (characters: %d)' % len(document.actions)
                    else: print 'Warning: Actions section was empty.'
                else:
                    #print 'adding action line'
                    document.actions += line

            # only match on the beginning of the name attribute, not
            # all documents are consistent-- some have numbers
            # appended, others have punctuation.
            elif links_section.match(line.strip()):
                state['links'] = True
        
            elif state['links']:
                # this is always (so far!) the last section (?)
                if line.find("</div>") >= 0 or line.find("</body>") >= 0:
                    state['links'] = False
                    state['finished'] = True
                    if len(document.links) > 0:
                        print '\nExtracted Links (characters: %d)' % len(document.links)

                    else: print 'Warning: Links section was empty.'
                    continue
                else:
                    document.links += line

            elif state['finished']:
                break

###########################################################
# Document Saving
###########################################################

save(documents)
print '\nProcessing Finished'
