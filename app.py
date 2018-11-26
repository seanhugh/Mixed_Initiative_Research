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

from flask import Flask, render_template, request, url_for
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def show_index():
  if request.method == 'GET':
    return render_template("index.html")
  else:
    myData = request.form['equation']
    return render_template("equation.html", data = myData)
    # return render_template("equation.html", data = myData)

