# File test_dehr_parser.py

import unittest

from dehr_parser import *


class InitialTest(unittest.TestCase):
    def test_platform_versions(self):
        check_versions()


#============================== If Name Is Main ===============================#

if __name__ == '__main__':
    unittest.main()
