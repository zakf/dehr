DEHR Readme.txt:


#================================ Simple Tasks ================================#

# How to setup the environment on my MBP 2013:

mac> cd ~/progs/dehr

mac> venv dehr              # Activate the virtualenv VE

(dehr)mac> 


# Run the Python unit tests:

(dehr)mac> ./test.sh        # This will autocomplete nicely

..........
----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK


# Build the website, output HTML ready for upload:

(dehr)mac> ./make.sh        # This will autocomplete nicely

Compiled page_test_01.html.

# Done.


#================================== Next Up ===================================#

These are To-Do items:

1. Currently, text in the source files is NOT parsed by the Django template engine. Change this. I need to create the Template objects dynamically by combining two files:
    ~/progs/dehr/source/templates/base.html
    ~/progs/dehr/source/pages/{{ filename }}.html


#================================= Resources ==================================#

How to manually compile Template objects and configure Engine objects:
    https://docs.djangoproject.com/en/1.9/ref/templates/api/
    Title: The Django template language: for Python programmers
