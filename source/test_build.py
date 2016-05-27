# File test_build.py

import unittest

from build import *


class InitialTest(unittest.TestCase):
    def test_platform_versions(self):
        check_versions()


class AllPageDataTest(unittest.TestCase):
    def test_all_page_data_part_init(self):
        with self.assertRaisesRegexp(BuildError, 'NEEDS a Boolean'):
            AllPageDataPart(None)


#============================== If Name Is Main ===============================#

if __name__ == '__main__':
    unittest.main()
