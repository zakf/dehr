# File dehr_helpers.py

class DehrError(Exception):
    """A base Exception class, make sub-classes for specific modules"""
    
    def __init__(self, description, more=''):
        self.description = description
        self.more = more
    
    def __str__(self):
        if self.more:
            return "%s:\n%s" % (self.description, self.more)
        else:
            return self.description
