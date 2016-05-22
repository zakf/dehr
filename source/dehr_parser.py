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

class CrCharacterError(DehrError):
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
    
    if '\r' in input_str:
        raise CrCharacterError(
            "There was at least one CR character in the input, but this is "
            "forbidden. You may NOT use CR characters. Here is the beginning "
            "of the offending string:\n\n%r" % input_str[0:60])
    
    input_str2 = deal_with_final_newlines(input_str)
    input_str3 = deal_with_excess_newlines(input_str2)
    
    tokens = []
    remainder = input_str3
    
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


def deal_with_final_newlines(input_str):
    """Remove all LF characters from the end of input_str
    
    The function lexer() chokes if input_str ends in a newline character. Writing regexes that handle terminal newline(s) correctly is VERY HARD, so I won't even attempt it.
    
    We will remove any number of final newline characters and output a string that ends in a DIFFERENT character.
    
    """
    
    done = False
    
    while (not done):
        if input_str[-1] == '\n':
            input_str = input_str[:-1]
        else:
            done = True
    
    return input_str


excess_newlines_pat = re.compile(r"[\n]{3,}")

def deal_with_excess_newlines(input_str):
    """The parser chokes if there are 3+ LF characters in a row
    
    Whenever you see 3+ LF characters in a row, replace with exactly 2 LF characters to avoid problems.
    
    """
    
    return excess_newlines_pat.sub('\n\n', input_str)


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


def unescape_double_newline(input_token_list):
    """Finds all '\[LF][LF]' tokens and removes the \ escape character
    
    Input:
        input_token_list:   List of tokens (strings).
    
    Output:
        clean_token_list:   List of tokens (strings).
    
    """
    
    clean_token_list = []
    for token in input_token_list:
        if token == '\\\n\n':
            clean_token_list.append('\n\n')
        else:
            clean_token_list.append(token)
    return clean_token_list


class OneLineNode(Node):
    """A nonterminal node
    
    Matches one line of raw input text, usually.
    
    Matches multiple lines if there is a single [LF] character in the middle. Also matches multipel lines if there is an ESCAPED sequence of two [LF] characters, i.e. '\[LF][LF]' with a backslash.
    
    """
    
    def parse(self):
        if self.input[0] == '<':
            # This is a NonParagraphLineNode.
            self.children = [TerminalNode(['<'])]
            child_input = unescape_double_newline(self.input[1:])
            self.children.append(NonParagraphLineNode(child_input))
        
        elif self.input[0] == '\\<':
            # This is a OneParagraphNode.
            child_input = ['<']         # We remove the \ escape character
            more_input = unescape_double_newline(self.input[1:])
            child_input.extend(more_input)
            self.children = [OneParagraphNode(child_input)]
        
        else:
            # This is a OneParagraphNode.
            child_input = unescape_double_newline(self.input)
            self.children = [OneParagraphNode(child_input)]
        
        for child in self.children:
            child.parse()
    
    def render(self):
        output = []
        for child in self.children:
            child.render()
            output.extend(child.output)
        self.output = output


class MultiParagraphNode(Node):
    """A nonterminal node
    
    Matches one or more paragraphs or non-paragraph lines.
    
    Modeled after zml.parser.RegularTextNode.
    
    """
    
    def parse(self):
        self.children = []
        while self.input:
            self.parse_chunk()
        for child in self.children:
            child.parse()
    
    def parse_chunk(self):
        if '\n\n' in self.input:
            # This contains two or more OneLineNodes.
            break_index = self.input.index('\n\n')
            first_child = OneLineNode(self.input[:break_index])
            second_child = TerminalNode([self.input[break_index]])
            self.children.append(first_child)
            self.children.append(second_child)
            next_index = break_index + 1
            self.input = self.input[next_index:]
        else:
            # This contains exactly one OneLineNode.
            self.children.append(OneLineNode(self.input))
            self.input = []
    
    def render(self):
        output = []
        for child in self.children:
            child.render()
            output.extend(child.output)
        self.output = output
