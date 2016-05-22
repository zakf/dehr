# File test_dehr_parser.py

from exceptions import IndexError
import unittest

from dehr_parser import *


class RegexTest(unittest.TestCase):
    def test_lexer_regexes(self):
        """Demonstrate the behavior of re.MatchObject (mtch)"""
        
        input = "<"
        mtch = token_pat.search(input)
        
        # Access a group that DID match:
        self.assertEqual(mtch.group("special"), "<")
        
        # Access groups that did NOT match:
        self.assertEqual(mtch.group("other"), None)
        self.assertEqual(mtch.group("next_special"), None)
        
        # Accessing a non-existent group raises an error:
        with self.assertRaises(IndexError):
            print mtch.group("fake_group_name")
    
    def test_lexer_regexes2(self):
        input = "\n\nFoo bar."
        mtch = token_pat.search(input)
        self.assertEqual(mtch.group("special"), "\n\n")
        
        input2 = "\\\n\nFoo bar."
        mtch2 = token_pat.search(input2)
        self.assertEqual(mtch2.group("special"), "\\\n\n")
        
        input3 = "Foo bar.\n\n"
        mtch3 = token_pat.search(input3)
        self.assertEqual(mtch3.group("special"), None)
        self.assertEqual(mtch3.group("other"), "Foo bar.")
        self.assertEqual(mtch3.group("next_special"), "\n\n")


class LexerTest(unittest.TestCase):
    def test_lexer(self):
        input = "<h1>Heading</h1>\n\nFirst.\n\nSecond.<b>Bold.</b>."
        tokens = lexer(input)
        self.assertEqual(tokens, [
            '<', 
            'h1>Heading', 
            '<', 
            '/h1>', 
            '\n\n', 
            'First.', 
            '\n\n', 
            'Second.', 
            '<', 
            'b>Bold.', 
            '<', 
            '/b>.'])


class ParserTest(unittest.TestCase):
    def test_parser(self):
        input = "<h1>Heading</h1>\n\nFirst.\n\nSecond.\n"
        tokens = lexer(input)
        node = MultiParagraphNode(tokens)
        node.parse()
        node.render()
        self.assertEqual(
            ''.join(node.output),
            "<h1>Heading</h1>\n\n<p>\nFirst.\n</p>\n\n<p>\nSecond.\n</p>")


#============================== If Name Is Main ===============================#

if __name__ == '__main__':
    unittest.main()
