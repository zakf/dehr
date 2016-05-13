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
