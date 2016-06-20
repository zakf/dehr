DEHR Readme.txt:

The latest GitHub committed version is available here, but it may take several minutes to update and I don't always push changes to GitHub:

https://rawgit.com/zakf/dehr/master/build/index.html


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

[DONE] 1. Currently, text in the source files is NOT parsed by the Django template engine. Change this. I need to create the Template objects dynamically by combining two files:
    ~/progs/dehr/source/templates/base.html
    ~/progs/dehr/source/pages/{{ filename }}.html

2. Template tag {% wiki 'Lexapro' %} that will create a link to Wikipedia.

3. Template tag {% self 'Lexapro' %} that will create a link to the page 'Lexapro' within the DEHR website. I am not sure about the name for the tag, I think 'self' might not be a good name.

4. {% clearfix %} template tag, outputs <div class="clearfix">.</div>.

5. Automatically put a Wikipedia link of every single page to that page's topic.

6. Make it a TINY BIT more beautiful.

7. Make it compatible with both Python 3.x and Python 2.7.x, see here:
   http://stackoverflow.com/questions/5937251/

8. Put it on GitHub.

9. {% indent %} makes <div class="indent"> and {% endindent %} similarly.

9.5. Maybe necessary, maybe not: {% try_link %} tag, which TRIES to make a link to 'target', but iff UrlLookupError then it just makes it plain flat text. This will be used in (10) below.

10. Metadata in the infobox should get a {% link %} tag iff possible. So if we have this:
    Neurotransmitters: DA, NE, 5-HT.
Then each of those three abbreviations should be a {% link %} internal hyperlink to the correct page.


#================================= Resources ==================================#

How to manually compile Template objects and configure Engine objects:
    https://docs.djangoproject.com/en/1.9/ref/templates/api/
    Title: The Django template language: for Python programmers
