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
    
    def test_deal_with_excess_newlines(self):
        input1 = "First\nSecond"
        output1 = deal_with_excess_newlines(input1)
        self.assertEqual(input1, output1)
        
        input2 = "First\n\nSecond"
        output2 = deal_with_excess_newlines(input2)
        self.assertEqual(input2, output2)
        
        input3 = "First\n\n\nSecond"
        output3 = deal_with_excess_newlines(input3)
        self.assertEqual(input2, output3)
        self.assertNotEqual(input3, output3)
        
        input4 = "First\n\n\n\nSecond"
        output4 = deal_with_excess_newlines(input4)
        self.assertEqual(input2, output4)
        self.assertNotEqual(input4, output4)
    
    def test_error_on_cr_chars(self):
        input = "This Is the Title\n\nFirst.\r\n\r\nSecond."
        with self.assertRaises(CrCharacterError):
            tokens = lexer(input)


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
    
    def test_parser2(self):
        input = """<h1>Heading Line</h1>

First.

Second paragraph.

<h2>Heading</h2>

Third.




Fourth.
Still fourth.

\<h2>Fifth,</h2> this was escaped.
"""
        tokens = lexer(input)
        node = MultiParagraphNode(tokens)
        node.parse()
        node.render()
        output = ''.join(node.output)
        self.assertEqual(
            output,
            """<h1>Heading Line</h1>\n\n<p>\nFirst.\n</p>\n\n<p>\nSecond paragraph.\n</p>\n\n<h2>Heading</h2>\n\n<p>\nThird.\n</p>\n\n<p>\nFourth.\nStill fourth.\n</p>\n\n<p>\n<h2>Fifth,</h2> this was escaped.\n</p>""")
    
    def test_parser3(self):
        input = """<h1>Heading</h1>

First.\\

Still first, I escaped the prior two LF characters.

Second paragraph here.

<b>Non-paragraph</b> because of the bold tags.

Third.

"""
        tokens = lexer(input)
        node = MultiParagraphNode(tokens)
        node.parse()
        node.render()
        output = ''.join(node.output)
        self.assertEqual(
            output,
            """<h1>Heading</h1>\n\n<p>\nFirst.\n\nStill first, I escaped the prior two LF characters.\n</p>\n\n<p>\nSecond paragraph here.\n</p>\n\n<b>Non-paragraph</b> because of the bold tags.\n\n<p>\nThird.\n</p>""")
    
    def test_parser4(self):
        input = """This Is the Title

First paragraph here.

Second paragraph.

<h2>Heading, not a paragraph</h2>

Third paragraph, end of file.

"""
        tokens = lexer(input)
        node = WholePageNode(tokens)
        node.parse()
        node.render()
        with self.assertRaisesRegexp(ParserError, 'have a node\.output'):
            node.output
        self.assertEqual(node.title, 'This Is the Title')
        self.assertEqual(node.content, """<p>
First paragraph here.
</p>

<p>
Second paragraph.
</p>

<h2>Heading, not a paragraph</h2>

<p>
Third paragraph, end of file.
</p>""")


#============================== If Name Is Main ===============================#

if __name__ == '__main__':
    unittest.main()
