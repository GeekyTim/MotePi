# Let's create a dictionary, the functional way

# Create your dictionary class
class dictionary(dict):
    ''' Create an expandable dictionary '''

    # __init__ function
    def __init__(self):
        ''' Initialise the dictionary '''
        self = dict()

    def add(self, key, value):
        ''' Add a new key value pair '''
        self[key] = value
