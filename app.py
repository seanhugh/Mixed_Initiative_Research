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
from random import shuffle
import time

import model

app = Flask(__name__)

# XXX unused by experimental setup
@app.route('/', methods=['GET', 'POST'])
def show_index():
  if request.method == 'GET':
    logfile.write(str(time.time()) + ": INDEX GET: EXPERIMENT GONE WRONG!!!\n")
    # begin.html, empty mathquill entry
    return render_template('begin.html')

  else:
    logfile.write(str(time.time()) + ": INDEX POST START: EXPERIMENT GONE WRONG!!!\n")
    # render view.html with initial state baked in
    startEquation = request.form['equation']
    startActive = request.form['active']
    print("got equation: " + startEquation)
    print("got active: " + startActive)

    startState = model.init(startEquation, startActive)

    print("start is: " + str(startState))
    logfile.write(str(time.time()) + ": START STATE IS " + str(startState) + "\n")

    return render_template('view.html', state=startState)

@app.route('/update', methods=['POST'])
def update_model():
  global state
  
  logfile.write(str(time.time()) + ": UPDATE POST\n")

  viewUpdate = request.get_json()
  print("got update: " + str(viewUpdate))

  nextState = model.update(viewUpdate["action"], viewUpdate["state"])

  print("update is: " + str(nextState))
  logfile.write(str(time.time()) + ": UPDATED STATE IS " + str(nextState) + "\n")

  return flask.jsonify(nextState)


#### Experimental Setup ####

active_list = [True, False]
problem_list_1 = [1, 2]
problem_list_2 = [3, 4]

# XXX restart server after each experiment!
shuffle(active_list)
shuffle(problem_list_1)
shuffle(problem_list_2)

problem_list = [problem_list_1[0], problem_list_2[0], problem_list_1[1], problem_list_2[1]]

logfile = open("log" + str(time.time()) + ".txt", "a")

logfile.write(str(time.time()) + ": STARTING WITH ACTIVES " + str(active_list) + "\n")
logfile.write(str(time.time()) + ": STARTING WITH PROBLEMS " + str(problem_list) + "\n")

# Set the order of equations

# Set continue from 1 -> 2, 2 -> intro2, 3 -> 4, 4 -> finish

# A survey screen
@app.route('/survey/<path>', methods=['GET'])
def show_survey(path):
  logfile.write(str(time.time()) + ": SHOW SURVEY, path: " + path + "\n")

  if path == "beg":
    text = "Thank you for participating in our research project! Please answer all of the below questions and click SUBMIT before proceeding to the next page."
    title = "Pre-Task Questionnaire"
    link_loc = "/text/vid1"
    data = {"text": text,
            "title": title,
            "link": link_loc}
    return render_template('survey_intro.html', data = data)

  text = "Thank you for solving those problems! Please answer all of the below questions and click SUBMIT before proceeding to the next page."
  title = "Post-Task Questionnaire " + str(path)
  if path == "1":
    link_loc = "/text/intro2"
    if active_list[0] == True:
      form_link = "https://docs.google.com/forms/d/e/1FAIpQLSdu4JIAQMew4SEO9UQ_5udRfrnraWr7CaGfJBtxHJucy_SANA/viewform?embedded=true"
    else:
      form_link = "https://docs.google.com/forms/d/e/1FAIpQLSel3Nkn2CfxoEHevEl63i6_zaT4jt-tUzfKCVz4H68fkZ9Ifg/viewform?embedded=true"
  else:
    link_loc = "/text/fin"
    if active_list[1] == True:
      form_link = "https://docs.google.com/forms/d/e/1FAIpQLSdu4JIAQMew4SEO9UQ_5udRfrnraWr7CaGfJBtxHJucy_SANA/viewform?embedded=true"
    else:
      form_link = "https://docs.google.com/forms/d/e/1FAIpQLSel3Nkn2CfxoEHevEl63i6_zaT4jt-tUzfKCVz4H68fkZ9Ifg/viewform?embedded=true"

  data = {"text": text,
          "title": title,
          "link": link_loc,
          "form_link": form_link}

  return render_template('survey.html', data = data)

# A text Screen
@app.route('/text/<part>', methods=['GET'])
def show_text(part):
  logfile.write(str(time.time()) + ": SHOW TEXT, part: " + part + "\n")

  if(part == "vid1"):
    text = "This experiment compares two versions of a user interface for a computer algebra system. We will provide two problems to solve for each version. You may use pen and paper along with the tools. Below is a video that demonstrates how to interact with these tools:"

    data = {"text": text,
            "title": "Experiment Explanation",
            "link": "/text/intro1"}

    return render_template('vid.html', data = data)

  if(part == "intro1"):
    #DO THE INTRO STUFF
    # continue button: 1
    text = "We will now present you with two problems to solve. Please solve them to the best of your ability. Please use only the provided tool and pen and paper to find your solutions. When you are ready, click 'Continue' to begin!"

    data = {"text": text,
            "title": "Intro pt. 1",
            "link": "/experiment/1"}

    return render_template('text.html', data = data)

  if(part == "intro2"):
    #DO THE INTRO STUFF
    # continue button: 3

    text = "We will now present you with two problems to solve. Please solve them to the best of your ability. Please use only the provided tool and pen and paper to find your solutions. When you are ready, click 'Continue' to begin!"

    data = {"text": text,
            "title": "Intro pt. 2",
            "link": "/experiment/3"}

    return render_template('text.html', data = data)

  if(part == "fin"):
    #DO THE INTRO STUFF
    # continue button: 3

    text = "Thank you for participating in our user study! Now redeem your insomnia cookie!"

    data = {"text": text,
            "title": "Finish",
            "link": "/experiment/fin"}

    logfile.close()

    return render_template('textNo.html', data = data)

# The equation modifier
@app.route('/experiment/<part>', methods=['POST', 'GET'])
def show_1(part):
  if request.method == 'GET':
    logfile.write(str(time.time()) + ": EXPERIMENT GET, part: " + part + "\n")

    if(part in ["1","2","3","4"]):
      # Set the title for the top of the screen
      title = part

      # Set the link location
      if part == "1":
        link_loc = "/experiment/2"
      elif part == "2":
        link_loc = "/survey/1"
      elif part == "3":
        link_loc = "/experiment/4"
      elif part == "4":
        link_loc = "/survey/2"

      problem_text = render_template('problem' + part + '.html')

      data = {"title": title,
              "link": link_loc,
              "problem": problem_text}

      return render_template('enterEquation.html', data = data)

  else:
    logfile.write(str(time.time()) + ": EXPERIMENT POST, part: " + part + "\n")

    if(part in ["1","2","3","4"]):
      #DO THE EQUATION SOLVING STUFF
      # Set the equation
      startEquation = request.form['equation']

      # Set the title for the top of the screen
      title = part

      # Set the link location
      if part == "1":
        link_loc = "/experiment/2"
        isActive = active_list[0]
      elif part == "2":
        link_loc = "/survey/1"
        isActive = active_list[0]
      elif part == "3":
        link_loc = "/experiment/4"
        isActive = active_list[1]
      elif part == "4":
        link_loc = "/survey/2"
        isActive = active_list[1]

      startState = model.init(startEquation, isActive)

      problem_text = render_template('problem' + part + '.html')

      data = {"title": title,
              "link": link_loc,
              "problem": problem_text}

      # return template
      return render_template('view2.html', state=startState, data=data)


if __name__ == "__main__":
  app.run()
