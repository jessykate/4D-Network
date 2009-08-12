try:
    import json
except: 
    try: 
        import simplejson as json
    except: 
        print 'Error: no json module installed.'
        sys.exit()


class Document(object):
    def __init__(self):
        self.challenge = ''
        self.subgoals = {}
        self.summary = ''
        self.actions = ''
        self.links = ''

class DocumentEncoder(json.JSONEncoder):
    ''' a custom JSON encoder for document objects '''
    def default(self, document):
        if not isinstance (document, Document):
            print 'Error: Cannot use the JSON DocumentEncoder for a non-document object.'
            return
        return {'challenge': document.challenge, 
                'subgoals': document.subgoals,
                'summary': document.summary,
                'actions': document.actions,
                'links': document.links,
                }


class DocumentDecoder(json.JSONDecoder):
    def decode(self, json_string):
        ''' call this function as the value of cls in the json.loads()
        function. it will return an actual Decode object. '''

        # use json's generic decode capability to parse the string
        # into a python dictionary.
        document_dict = json.loads(json_string)

        # get messages back first:    
        document = Document()
        document.challenge = document_dict['challenge']
        document.subgoals = document_dict['subgoals']
        document.summary = document_dict['summary']
        document.actions = document_dict['actions']
        document.links = document_dict['links']

        return document

