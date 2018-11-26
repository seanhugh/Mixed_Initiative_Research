### HOW TO KILL LOST APP ###

# How to kill flask:
# ps -ef | grep python
# kill -9 ID

### STRUCTURE OF FOLDER ###

#/app
#    - app.py
#    /templates
#        - index.html
#        - equation.html
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
import flask
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def show_index():
  if request.method == 'GET':
    print('get index')
    return render_template('begin.html')
  else:
    print('post begin')
    myData = request.form['equation']
    return render_template('view.html', data = {"equation" : myData})

state = 0

@app.route('/update', methods=['POST'])
def update_model():
  global state
  print('update')
  myData = request.get_json()
  state += 1
  print(myData)
  return flask.jsonify({"equation" : str(state)})

