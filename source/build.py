# File build.py:
# 
# This is the key Python scrip in the DEHR package. It compiles the data using 
# the templates and outputs static HTML to the 'build' directory.

import argparse
import textwrap
import os
import sys
import re
from collections import OrderedDict

import django
import django.template
Context = django.template.Context

from dehr_helpers import *
import dehr_parser


class BuildError(DehrError):
    pass

class UrlLookupError(DehrError):
    pass


build_file_path = os.path.abspath(__file__)
# build_file_path == '/Users/zakf/progs/dehr/source/build.py'
source_dir_path = os.path.dirname(build_file_path)  # Chops off '/build.py'
BASE_DIR = os.path.dirname(source_dir_path)         # Chops off '/source'
# BASE_DIR == '/Users/zakf/progs/dehr'


#======================== Command Line Argument Parser ========================#

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent("""\
    Builds the Static Website
    
    This is the script build.py, it is the key Python script in the DEHR 
    software package. It compiles the data using the templates and outputs 
    static HTML to the 'build' directory."""))

parser.add_argument('-b', '--build-all', action='store_true', 
                    help="Build the website")


#============================= Core Functionality =============================#

def check_versions():
    """Confirm that Python and Django are the correct versions
    
    Other versions may work, but by default unexpected versions will raise an error.
    
    """
    
    django_version = django.VERSION
    
    if (django_version[0] != 1) or (django_version[1] != 9):
        raise BuildError(
            "You must use Django 1.9.x. You are using Django %s." % 
            (django_version,))
    
    python_version = sys.version_info
    
    if python_version.major != 2:
        raise BuildError(
            "This script may not work with Python 3. You are probably using "
            "Python 3. Try Python 2.7.x instead.")
    
    if python_version.minor != 7:
        raise BuildError(
            "This script may only work with Python 2.7.x. You are using a "
            "different version of Python.")
    
    if python_version.micro < 10:
        raise BuildError(
            "Your version of Python is probably too old. Try 2.7.10 or newer.")


def make_engine(base_dir):
    """Make a Django template Engine instance
    
    See here:
    
    https://docs.djangoproject.com/en/1.9/ref/templates/api/
    
    """
    
    templates_dir = os.path.join(base_dir, 'source', 'templates')
    
    engine = django.template.Engine(
        dirs = [templates_dir],
        debug = True,
        libraries = {
            # Libraries mentioned here are accessible to the {% load %} tag, 
            # but they are NOT loaded automatically. The key on the left is 
            # a string that will be passed to {% load %} and the value on the 
            # right is a dotted Python path to a Python module.
            
            'dehr_template_tags': 'dehr_template_tags',
        },
    )
    
    return engine


# DEPRECATED, use dehr_parser.py instead:
def add_p_tags(raw_str, page_title):
    """Replace blank lines with HTML <p> tags
    
    The page_title argument is needed for the error messages.
    
    """
    
    mtch = re.search(r"(?<!\n)$", raw_str)
    if not mtch:
        raise BuildError(
            "The page '%s' ends with two or more newline characters. There "
            "should be exactly one newline at the end." % page_title)
    
    mtch2 = re.search(r"\n$", raw_str)
    if not mtch2:
        raise BuildError(
            "The page '%s' does not have a newline character at the end. "
            "please add exactly one newline at the end." % page_title)
    
    o = ['<p>\n']
    o.append(re.sub(r"\n\n", "\n</p>\n\n<p>\n", raw_str))
    o.append('</p>\n')
    
    return ''.join(o)


"""
For examples of hardcore regexes, see here:
    ~/Dropbox/iPhone/Current/Programming/
    Where_to_Find_Hardcore_Regexes_Regular_Expressions.txt

The DOTALL flag (?s) is very important. With DOTALL set, the . will match everything, including newline characters. Without this flag, . will NOT match newlines, and thus pattern matches will never be more than one line (unless you explicitly include \n in the pattern).
"""

# DEPRECATED: page_pat is deprecated, use dehr_parser.py instead:
page_pat = re.compile(r"""(?xs)     # x means VERBOSE, s means DOTALL.
^                       # Matches the beginning of the string.
(?P<page_title>.*?)\n   # The entire first line is the page title.
[ \n\r\t]               # Throw away any whitespace characters.
(?P<page_content>.*)    # The remainder of the file is matched here.
$                       # Matches the end of the string.
""")


def od_to_str(od, var_name):
    """Print an OrderedDict in a standardized format, return a string
    
    Arguments:
        od:         OrderedDict to be printed.
        
        var_name:   String, the variable name for this OrderedDict.
    
    """
    
    o = ['%s = OrderedDict([\n' % var_name]
    for key in od:
        o.append('    (%r, ' % key)
        o.append('%r),\n' % od[key])
    o.append('])\n')
    return ''.join(o)


class AllPageDataPart(object):
    """Holds all the page titles, page URLs, and page aliases
    
    See AllPageData for more information.
    
    Attributes:
        read_only:      Boolean, iff True then you SHOULD NOT edit this object.
    
    """
    
    def __init__(self, read_only):
        if not (type(read_only) is bool):
            raise BuildError(
                "The AllPageDataPart constructor NEEDS a Boolean for the one "
                "and only argument.")
        self.titles = OrderedDict()
        self.aliases = OrderedDict()
        self.read_only = read_only
    
    def add_title(self, title, page_filename):
        if self.read_only:
            raise BuildError("READ ONLY, you may not do this.")
        self.titles[title] = page_filename
    
    def add_alias(self, alt_name, page_filename):
        """This FORCES LOWERCASE as it adds the alt_name"""
        if self.read_only:
            raise BuildError("READ ONLY, you may not do this.")
        self.aliases[alt_name.lower()] = page_filename
    
    def get_titles(self):
        """Returns all keys from self.titles as a SORTED list of strings
        
        The OrdereDict self.titles is sorted by page_filename, which is not very useful when generating a list that a human will see. This returns a list of strings (just titles, no page_filenames) that is sorted by the human-readable title.
        
        """
        
        all_titles = []
        # The following line, with list() and .items(), ensures the SAME exact 
        # behavior in both Python 2.7.x and 3.x:
        unsorted_titles = list(self.titles.items())
        for title, page_filename in unsorted_titles:
            all_titles.append(title)
        return sorted(all_titles)


class AllPageData(object):
    """Holds all the page titles, page URLs, and page aliases
    
    This object is used by the {% link %} custom template tag.
    
    This object is also used in index.html to create a list of all the pages, by title.
    
    Attributes:
        prior.titles:   OrderedDict, one-to-one map from human-readable titles 
                        to page filenames. This is used to create a list of all pages. See example below.
                        
                        We do NOT force lowercase, we use proper case.
                        
                        We do NOT have duplicates, there is exactly one entry for each page. Every value is unique.
        
        prior.aliases:  OrderedDict, many-to-one map from aliases to page 
                        filenames. This is used by the {% link %} tag during lookups. See example below.
                        
                        We FORCE LOWERCASE in the keys. Thus, "Lexapro" may not appear as a key, it must be "lexapro". This is to facilitate lookups.
                        
                        We have TONS OF DUPLICATES. Thus, "lexapro", "cipralex", "s-citalopram", and "escitalopram" are four separate keys but they all have the same value, "lexapro.html".
        
        next.titles:    Similar to prior.titles, but this is created during 
                        rendering. Next time build.py runs, this will be used as prior.titles.
        
        next.aliases:   Similar to prior.aliases.
    
    Examples:
        
        prior.titles = OrderedDict([
            ('Cocaine', 'cocaine.html'),
            ('Escitalopram (Lexapro)', 'lexapro.html'),
            ('Sertraline (Zoloft)', 'zoloft.html'),
        ])
        
        prior.aliases = OrderedDict([
            ('cipralex', 'lexapro.html'),
            ('escitalopram', 'lexapro.html'),
            ('lexapro', 'lexapro.html'),
            ('s-citalopram', 'lexapro.html'),   # We forced LOWERCASE
            ('cocaine', 'cocaine.html'),
            ('coke', 'cocaine.html'),
            ('methyl benzoyl ecgonine', 'cocaine.html'),
        ])
    
    """
    
    def __init__(self):
        self.prior = AllPageDataPart(False)
        self.next = AllPageDataPart(False)
    
    def save_next(self, base_dir):
        """Create the file all_page_data.py using self.next"""
        next_str = self.next_to_str('all_page')
        apd_filepath = os.path.join(base_dir, 'source', 'all_page_data.py')
        apd_file = open(apd_filepath, 'wb')
        apd_file.write("# File: all_page_data.py\n# \n")
        apd_file.write("# This file was written by AllPageData.save_next().")
        apd_file.write("\n\n")
        apd_file.write(next_str)
        apd_file.close()
        print "Saved the AllPageData.next object to all_page_data.py."
    
    def load_prior(self, base_dir):
        """Populate self using the all_page_data.py file"""
        apd_filepath = os.path.join(base_dir, 'source', 'all_page_data.py')
        apd_file = open(apd_filepath, 'rb')
        apd_str = apd_file.read()
        apd_file.close()
        exec(apd_str)
        self.prior.titles = all_page_titles
        self.prior.aliases = all_page_aliases
        self.prior.read_only = True
    
    def add_title(self, title, page_filename):
        self.next.add_title(title, page_filename)
    
    def add_alias(self, alt_name, page_filename):
        self.next.add_alias(alt_name, page_filename)
    
    def get_titles(self):
        return self.prior.get_titles()
    
    def find_url(self, alt_name):
        """This will be used by the {% link %} custom template tag
        
        alt_name is a string like "Lexapro" or "S-citalopram", not necessarily lowercase. It will be forced into lowercase before the lookup occurs.
        
        Input example: "Lexapro"
        
        Output example: "lexapro.html"
        
        """
        
        alt_name_lowercase = alt_name.lower()
        page_filename = self.prior.aliases.get(alt_name_lowercase, None)
        if page_filename == None:
            # The alias alt_name is NOT in the list, lookup failed.
            raise UrlLookupError(
                "The search term '%s' did not match any aliases in "
                "AllPageData.prior.aliases. You may need to run build.py "
                "once more, because it uses an old cached list of aliases. "
                "Alternatively, look at all_page_data.py." % alt_name)
        return page_filename
    
    def next_to_str(self, var_name):
        o = [od_to_str(self.next.titles, '%s_titles' % var_name)]
        o.append('\n')
        o.append(od_to_str(self.next.aliases, '%s_aliases' % var_name))
        return ''.join(o)


def compile_one_page(base_dir, engine, apd, page_filename):
    """Compile and save one HTML file
    
    Arguments:
        base_dir:       String, usually BASE_DIR, e.g. "/Users/zakf/progs/dehr".
        
        engine:         django.template.Engine object.
        
        apd:            AllPageData object.
        
        page_filename:  String, e.g. "lexapro.html".
    
    TODO:
    Make this function more customizable. Currently, it only handles the template_file 'base.html' and it only handles the template context variables page_title and page_content. In the future, there might be a version where the template_file is 'one_drug.html' and the context variables include generic_names and brand_names and other stuff like that.
    
    """
    
    page_filepathname = os.path.join(base_dir, 'source', 'pages', page_filename)
    page_file = open(page_filepathname, 'rb')
    page_raw = page_file.read()
    page_file.close()
    
    if '\r' in page_raw:
        raise BuildError(
            "The file %s contains CR character(s), which is bad. Fix it." % 
            page_filename)
    
    if '\t' in page_raw:
        raise BuildError(
            "The file %s contains hard tab character(s), which is bad. "
            "Please fix it." % page_filename)
    
    tokens = dehr_parser.lexer(page_raw)
    whole_page_node = dehr_parser.WholePageNode(tokens)
    whole_page_node.parse()
    whole_page_node.render()
    wpn = whole_page_node
    
    meta_dict = whole_page_node.meta_dict   # An OrderedDict of metadata
    apd.add_title(wpn.title, page_filename)
    apd.add_alias(wpn.title, page_filename)
    if page_filename[-5:] == '.html':
        apd.add_alias(page_filename[:-5], page_filename)
    
    page_type = meta_dict.get('Page type', [None])[0]
    if not page_type:
        page_type = 'Not specified'
    
    def get_str_or_none(key):
        """Use this for keys which ALWAYS have just one value"""
        value_list = meta_dict.get(key, [])
        if len(value_list) == 1:
            return value_list[0]
        elif len(value_list) == 0:
            return None
        else:
            raise BuildError(
                "The meta_dict for the page '%s' is ill-formed. The key "
                "'%s' should have NO MORE THAN ONE value. It had 2 or "
                "more values. They are: %r" % 
                (page_filename, key, value_list))
    
    def get_list_or_empty(key):
        return meta_dict.get(key, [])
    
    wikipedia_name = get_str_or_none('Wikipedia name')
    
    ## This 'if' is unnecessary, it fails gracefully:
    # if page_type == 'One drug':
    brand_names = get_list_or_empty('Brand names')
    for brand_name in brand_names:
        apd.add_alias(brand_name, page_filename)
    generic_names = get_list_or_empty('Generic names')
    for generic_name in generic_names:
        apd.add_alias(generic_name, page_filename)
    related_names = get_list_or_empty('Related names')
    for related_name in related_names:
        apd.add_alias(related_name, page_filename)
    
    neurotransmitters = get_list_or_empty('Neurotransmitters')
    
    if (wikipedia_name or brand_names or generic_names or neurotransmitters or 
        related_names):
        has_metadata = True
    else:
        has_metadata = False
    
    ## Old method, cannot deal with Django template syntax in the page_file:
    # base_template = engine.get_template('base.html')
    
    templates_dir = os.path.join(base_dir, 'source', 'templates')
    template_filepathname = os.path.join(templates_dir, 'base.html')
    template_file = open(template_filepathname, 'rb')
    template_raw = template_file.read()
    template_file.close()
    
    # Insert the page_file code into the template_file code:
    template_str = template_raw.replace(
        '{{ page_content|safe }}',
        wpn.content)
    
    template_object = engine.from_string(template_str)
    context_object = Context({
        'page_title': wpn.title,
        # 'page_content': wpn.content,  # Now I do this manually, see above.
        'page_type': page_type,
        'wikipedia_name': wikipedia_name,
        'has_metadata': has_metadata,
        'brand_names': brand_names,
        'generic_names': generic_names,
        'related_names': related_names,
        'neurotransmitters': neurotransmitters,
        'mechanisms': get_list_or_empty('Mechanisms'),
        'drug_class': get_list_or_empty('Drug class'),
    })
    
    if page_type == 'Index':
        all_pages_list = []
        for page_title in apd.get_titles():
            all_pages_list.append([
                page_title,
                apd.find_url(page_title)])
        context_object['all_pages_list'] = all_pages_list
    
    rendered = template_object.render(context_object)
    
    out_filepathname = os.path.join(base_dir, 'build', page_filename)
    out_file = open(out_filepathname, 'wb')
    out_file.write(rendered)
    out_file.close()
    
    print "Compiled %s." % page_filename


#=============================== Test Functions ===============================#

def simple_test(engine):
    """A very simple test"""
    
    template_object = engine.get_template('simple_template_test.html')
    context_object = Context({'whose_children': 'Florey'})
    rendered = template_object.render(context_object)
    print rendered


def template_test02(engine):
    """This requires the extends tag"""
    
    template_object = engine.get_template('template_test02.html')
    context_object = Context({})
    rendered = template_object.render(context_object)
    print rendered


def template_test03(engine):
    """This uses base.html"""
    
    template_object = engine.get_template('base.html')
    context_object = Context({
        'page_title': "Template Test 03",
        'page_content': "<p>Paragraph one.</p><p>Paragraph two, dude.</p>",
    })
    rendered = template_object.render(context_object)
    print rendered


#============================== If Name Is Main ===============================#

if __name__ == '__main__':
    args = parser.parse_args()
    
    check_versions()
    
    if len(sys.argv) == 1:
        # No options were selected
        # The user simply invoked 'python build.py'
        # In this case, the script should do nothing
        
        print "You need to specify options, or else this script does nothing."
        print "Type 'python build.py -h' for more help."
        sys.exit()
    
    engine = make_engine(BASE_DIR)
    
    if args.build_all:
        # The option '-b' was set.
        
        ## Tests:
        ## 
        # simple_test(engine)
        # template_test02(engine)
        # template_test03(engine)
        # compile_one_page(BASE_DIR, engine, 'page_test_01.html')
        
        apd = AllPageData()
        apd.load_prior(BASE_DIR)
        pages_dir = os.path.join(BASE_DIR, 'source', 'pages')
        for page_filename in sorted(os.listdir(pages_dir)):
            if page_filename[-5:] == '.html':
                compile_one_page(BASE_DIR, engine, apd, page_filename)
        apd.save_next(BASE_DIR)
