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
    
    def test_apd_read_only(self):
        apdp = AllPageDataPart(True)
        self.assertEqual(apdp.read_only, True)
        with self.assertRaisesRegexp(BuildError, 'READ ONLY'):
            apdp.add_title('Escitalopram (Lexapro)', 'lexapro.html')
        apdp.read_only = False
        apdp.add_title('Escitalopram (Lexapro)', 'lexapro.html')
        apdp.add_title('Sertraline (Zoloft)', 'zoloft.html')
        apdp.add_title('Aaron Sorkin', 'zyzzylvaria.html')
        self.assertEqual(len(apdp.titles), 3)
        self.assertEqual(apdp.get_titles(), [
            'Aaron Sorkin',
            'Escitalopram (Lexapro)',
            'Sertraline (Zoloft)'])
    
    def test_apd_find_url(self):
        apd = AllPageData()
        apd.add_alias('LEXApro', 'lexapro.html')
        apd.add_alias('escitalopram', 'lexapro.html')
        self.assertEqual(len(apd.next.aliases), 2)
        apd.prior.aliases = apd.next.aliases.copy()
        self.assertEqual(apd.find_url('lexapro'), 'lexapro.html')
        self.assertEqual(apd.find_url('lexaPRO'), 'lexapro.html')
        self.assertEqual(apd.find_url('escitaLOPram'), 'lexapro.html')
        with self.assertRaisesRegexp(UrlLookupError, 'all_page_data.py'):
            apd.find_url('not_in_the_dict')
    
    def test_next_to_str(self):
        apd = AllPageData()
        apd.add_title('Olanzapine (Zyprexa)', 'zyprexa.html')
        apd.add_title('Ziprasidone (Geodon)', 'geodon.html')
        apd.add_alias('Olanzapine', 'zyprexa.html')
        apd.add_alias('Zyprexa', 'zyprexa.html')
        apd.add_alias('Ziprasidone', 'geodon.html')
        apd.add_alias('Geodon', 'geodon.html')
        self.assertEqual(
            apd.next_to_str('bunny_ocean'),
            """bunny_ocean_titles = OrderedDict([
    ('Olanzapine (Zyprexa)', 'zyprexa.html'),
    ('Ziprasidone (Geodon)', 'geodon.html'),
])

bunny_ocean_aliases = OrderedDict([
    ('olanzapine', 'zyprexa.html'),
    ('zyprexa', 'zyprexa.html'),
    ('ziprasidone', 'geodon.html'),
    ('geodon', 'geodon.html'),
])
""")


#============================== If Name Is Main ===============================#

if __name__ == '__main__':
    unittest.main()
