# File build.py:
# 
# This is the key Python scrip in the DEHR package. It compiles the data using 
# the templates and outputs static HTML to the 'build' directory.

import argparse
import textwrap
import os
import sys
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


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent("""\
    Builds the Static Website
    
    This is the script build.py, it is the key Python script in the DEHR 
    software package. It compiles the data using the templates and outputs 
    static HTML to the 'build' directory."""))

parser.add_argument('-b', '--build-all', action='store_true', 
                    help="Build the website")


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
        
        # simple_test(engine)
        # template_test02(engine)
        template_test03(engine)
