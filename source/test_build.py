# File test_build.py

import unittest

from build import *


class InitialTest(unittest.TestCase):
    def test_platform_versions(self):
        check_versions()


#============================== If Name Is Main ===============================#

if __name__ == '__main__':
    unittest.main()
