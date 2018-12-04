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

from flask import Flask, render_template, request, url_for
import flask
import os

import model

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def show_index():
  if request.method == 'GET':
    # begin.html, empty mathquill entry
    return render_template('begin.html')

  else:
    # render view.html with initial state baked in
    startEquation = request.form['equation']
    startActive = request.form['active']
    print("got equation: " + startEquation)
    print("got active: " + startActive)

    startState = model.init(startEquation, startActive)

    return render_template('view.html', state=startState)

@app.route('/update', methods=['POST'])
def update_model():
  global state

  viewUpdate = request.get_json()
  print("got update: " + str(viewUpdate))

  nextState = model.update(viewUpdate["action"], viewUpdate["state"])
  print("update is: " + str(nextState))

  return flask.jsonify(nextState)


if __name__ == "__main__":
  app.run()
