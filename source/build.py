# File build.py:
# 
# This is the key Python scrip in the DEHR package. It compiles the data using 
# the templates and outputs static HTML to the 'build' directory.

import argparse
import textwrap
import sys


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent("""\
    Builds the Static Website
    
    This is the script build.py, it is the key Python script in the DEHR 
    software package. It compiles the data using the templates and outputs 
    static HTML to the 'build' directory."""))

parser.add_argument('-b', '--build', action='store_true', 
                    help="Build the website")


if __name__ == '__main__':
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        # No options were selected
        # The user simply invoked 'python build.py'
        # In this case, the script should do nothing
        
        print "You need to specify options, or else this script does nothing."
        print "Type 'python build.py -h' for more help."
        sys.exit()
