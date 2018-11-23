### HOW TO KILL LOST APP ###

# How to kill flask:
# ps -ef | grep python
# kill -9 ID

### STRUCTURE OF FOLDER ###

#/app
#    - app.py
#    /templates
#        - index.html
#    /static
#        /css
#            - styles.css
#        /js
#        /img

### STRUCTURE OF THE JSON
#
# DISPLAY JSON:
# eq: equation in latek
# tree: the current tree
# location: location within the tree
# buttons: list of buttons (use IDS for buttons)
#
# ACTION JSON:
# Button clicked: id of button clicked
# Location in tree: location of cursor within tree

from flask import Flask, render_template, request, url_for
import os

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def show_index():
    return render_template("index.html")
