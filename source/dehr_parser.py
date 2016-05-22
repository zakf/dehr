# File dehr_parser.py
# 
# This is a lexer and parser for pseudo-HTML templates.
# 
# This file is modeled after this earlier file:
#     ~/progs/zml/trunk/zml/parser.py

import re

from dehr_helpers import *


class ParserError(DehrError):
    pass


#=========================== Regexes for the Lexer ============================#

# The escape character is \ which is the backslash.

special_tokens = r"""
    # First, we will search for escaped special sequences. In regexes, terms 
    # separated by | (OR) are searched from left to right, and the first match 
    # is automatically accepted. That means that if an escaped sequence 
    # exists, it will be matched before an unescaped sequence is even searched 
    # for. Here are the escape sequences:
    
    (?:\\<)|            # Matches "\<", which is an escaped <
    (?:\\[\n]{2})|      # Matches "\[LF][LF]"
    
    # Next, we search for unescaped special sequences:
    
    (?:<)|              # The opening of an HTML tag
    (?:\n\n)            # Two newlines in a row
    
    # NOTE: It does NOT end in a | (OR).
"""


token_pat = re.compile(r"""(?xs)                # x: Verbose, s: DOTALL
    ^                                           # Require start of string
    (?P<special>""" + special_tokens + r""")    # Match special tokens
    |
    (?:
      (?P<other>.*?) # Iff the string doesn't start with a special token, then 
                     # we put all the non-special stuff in 'other'.
      (?P<next_special>""" + special_tokens + r"""  # Find the next special
        |$  # Maybe the input ends, store that in 'next_special' too.
      )
    )""")


#================================== Grammar ===================================#

"""
Let's define the grammar for our parser.

See the Wikipedia article "formal grammar" for terminology and notation:
https://en.wikipedia.org/wiki/Formal_grammar

WholePageNode  -->  TitleNode  '\n\n'  MultiParagraphNode
    
    # The rule above may be made more complex to accommodate things like 
    # alternate page titles, page title redirects, and tags, all of which would 
    # go just under the title (TitleNode), which is the first line of the file.

MultiParagraphNode  -->  OneLineNode  ('\n\n'  MultiParagraphNode)?
    
    # The rule above uses right recursion, also known as tail recursion. This 
    # is the opposite of left recursion. I think tail recursion is easier to 
    # implement, but I am not sure.

OneLineNode  -->  '<'  NonParagraphLineNode         # Do NOT wrap in <p> tags

OneLineNode  -->  '\<'  OneParagraphNode            # DO wrap in <p> tags

OneLineNode  -->  OneParagraphNode                  # DO wrap in <p> tags

"""


#=================================== Lexer ====================================#

def lexer(input_str):
    """The lexer takes in a raw pseudo-HTML string and outputs a list of tokens
    
    Arguments:
        input_str:  String, raw pseudo-HTML.
    
    Returns:
        token_list: A list of strings, each string is a token.
    
    """
    
    tokens = []
    remainder = input_str
    
    while remainder:
        mtch = token_pat.match(remainder)
        if mtch == None:
            raise ParserError(
                "VERY weird, token_pat did not find a match.\n"
                "tokens = %r\n"
                "remainder = %r\n"
                "input_str = %r" % (tokens, remainder, input_str))
        if mtch.group("special"):
            # The remainder starts with a special token:
            tokens.append(mtch.group("special"))
            remainder = remainder[mtch.end("special"):]
        else:
            # The remainder does NOT start with a special token:
            tokens.append(mtch.group("other"))
            remainder = remainder[mtch.end("other"):]
    
    return tokens


#=================================== Parser ===================================#

class Node(object):
    """A fully-parsed input is a branched tree of Nodes
    
    Attributes:
        children:   List of Nodes or None. Iff this is a terminal Node, then 
                    children == None. Iff this is a nonterminal Node, then children is a list of Nodes, or more precisely, it is a list of objects that inherit from Node.
        input:      List of tokens (strings), all the raw input that 
                    produced this Node.
        output:     List of strings, all the raw HTML to be output in its 
                    final form. Just concatenate the output and you are done.
    
    Methods:
        parse:          First function to get called. It looks at self.input 
                        and (generally) turns the input into one or more Nodes, and those Nodes are stored in self.children. Then, node.parse() is called on each of the child Nodes. The exception is iff this will become a TerminalNode, in which case the input is NOT turned into any Nodes and self.children == None.
        render:         Last function to get called. It turns this Node into a 
                        string of output HTML, and the output string is stored in self.output. To do this, it must recursively call node.render() on each of its children.
    
    """
    
    def __init__(self, input):
        """The argument 'input' is a list of tokens (raw input strings)"""
        self.input = input


class TerminalNode(Node):
    """A terminal node
    
    Attributes:
        content:    String, NOT a list of strings (not a list of tokens).
    
    """
    
    def parse(self):
        if len(self.input) != 1:
            raise ParserError(
                "TerminalNode.parse() was called, but the TerminalNode's "
                "input was not exactly 1 token.\ninput = %r." % self.input)
        self.children = None
        self.content = self.input[0]
    
    def render(self):
        self.output = [self.content]


class OneParagraphNode(Node):
    """A type of terminal node
    
    When rendered, it will get wrapped in <p> tags.
    
    """
    
    def parse(self):
        if len(self.input) < 1:
            raise ParserError(
                "OneParagraphNode.parse() was called, but the input was not "
                "at least 1 token long.\ninput = %r." % self.input)
        self.children = None
    
    def render(self):
        self.output = ['<p>\n']
        self.output.extend(self.input)
        self.output.append('\n</p>')


class NonParagraphLineNode(Node):
    """A type of terminal node
    
    For example, a line that starts with <h1> will become a NonParagraphLineNode.
    
    When rendered, it will NOT get wrapped in <p> tags.
    
    """
    
    def parse(self):
        if len(self.input) < 1:
            raise ParserError(
                "NonParagraphLineNode.parse() was called, but the input was "
                "not at least 1 token long.\ninput = %r." % self.input)
        self.children = None
    
    def render(self):
        self.output = self.input[:]


class OneLineNode(Node):
    """A nonterminal node
    
    Matches one line of raw input text.
    
    """
    
    def parse(self):
        if self.input[0] == '<':
            # This is a NonParagraphLineNode.
            self.children = [TerminalNode(['<'])]
            self.children.append(NonParagraphLineNode(self.input[1:]))
        
        elif self.input[0] == '\\<':
            # This is a OneParagraphNode.
            self.children = [TerminalNode(['<'])]   # We remove the \ character
            self.children.append(OneParagraphNode(self.input[1:]))
        
        else:
            # This is a OneParagraphNode.
            self.children = [OneParagraphNode(self.input)]
        
        for child in self.children:
            child.parse()
