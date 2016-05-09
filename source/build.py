# File build.py:
# 
# This is the key Python scrip in the DEHR package. It compiles the data using 
# the templates and outputs static HTML to the 'build' directory.

import argparse
import textwrap
import os
import sys
import re

import django
import django.template
Context = django.template.Context

from dehr_helpers import *


class BuildError(DehrError):
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
        libraries = None,       # I will use this for custom tags
    )
    
    return engine


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

page_pat = re.compile(r"""(?xs)     # x means VERBOSE, s means DOTALL.
^                       # Matches the beginning of the string.
(?P<page_title>.*?)\n   # The entire first line is the page title.
[ \n\r\t]               # Throw away any whitespace characters.
(?P<page_content>.*)    # The remainder of the file is matched here.
$                       # Matches the end of the string.
""")


def compile_one_page(base_dir, engine, page_filename):
    """Compile and save one HTML file"""
    
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
    
    mtch = page_pat.search(page_raw)
    if not mtch:
        raise BuildError(
            "The page_pat regex did not match for the file %s." % 
            page_filename)
    
    page_title = mtch.group('page_title')
    page_content = mtch.group('page_content')
    page_content = add_p_tags(page_content, page_title)
    
    base_template = engine.get_template('base.html')
    context_object = Context({
        'page_title': page_title,
        'page_content': page_content})
    rendered = base_template.render(context_object)
    
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
        
        compile_one_page(BASE_DIR, engine, 'page_test_01.html')
