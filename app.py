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

    print("start is: " + str(startState))

    return render_template('view.html', state=startState)

@app.route('/update', methods=['POST'])
def update_model():
  global state

  viewUpdate = request.get_json()
  print("got update: " + str(viewUpdate))

  nextState = model.update(viewUpdate["action"], viewUpdate["state"])
  print("update is: " + str(nextState))

  return flask.jsonify(nextState)


#### Experimental Setup ####

# Doing experimental setup here (Could move this to another file later)
def makeState(equation, active):
  return {"equation": equation,
          "active": active}

# Create the four equations

# Randomize the order of the equations (in pairs)
# Randomize which group gets the alternative method (in pairs)

# To add in equations just edit the equations here, randomization will be
#  done automatically:


active_list = [True, False]

shuffle(active_list)

# Set the order of equations

# Set continue from 1 -> 2, 2-> intro2, 3-> 4, 4 -> finish

# A survey screen
@app.route('/survey/<path>', methods=['GET'])
def show_survey(path):

  if path == "beg":
    text = "Thank you for participating in our research project! Please answer ALL of the below questions, submit the form, then proceed to the next page. Thanks!"
    title = "Introduction Survey"
    link_loc = "/text/vid1"
    data = {"text": text,
              "title": title,
              "link": link_loc}
    return render_template('survey_intro.html', data = data)

  text = "This is some sample instructions"
  title = "Survey " + path
  if path == "1" :
    link_loc = "/text/intro2"
    if active_list[0] == True:
      form_link = "https://docs.google.com/forms/d/e/1FAIpQLSdu4JIAQMew4SEO9UQ_5udRfrnraWr7CaGfJBtxHJucy_SANA/viewform?embedded=true"
    else:
      form_link = "https://docs.google.com/forms/d/e/1FAIpQLSel3Nkn2CfxoEHevEl63i6_zaT4jt-tUzfKCVz4H68fkZ9Ifg/viewform?embedded=true"
  else:
    link_loc = "/text/fin"
    if active_list[1] == False:
      form_link = "https://docs.google.com/forms/d/e/1FAIpQLSel3Nkn2CfxoEHevEl63i6_zaT4jt-tUzfKCVz4H68fkZ9Ifg/viewform?embedded=true"
    else:
      form_link = "https://docs.google.com/forms/d/e/1FAIpQLSdu4JIAQMew4SEO9UQ_5udRfrnraWr7CaGfJBtxHJucy_SANA/viewform?embedded=true"

  data = {"text": text,
              "title": title,
              "link": link_loc,
              "form_link": form_link}

  return render_template('survey.html', data = data)

# A text Screen
@app.route('/text/<part>', methods=['GET'])
def show_text(part):
    if(part == "vid1"):
      text = "In this experiment we will be comparing two different equation solving tools. We will provide 2 different problems to solve for each tool. You are allowed to use pen & paper alongside with the tools. Below is a video that demonstrates how to interact with these tools:"

      data = {"text": text,
              "title": "Experiment Explanation",
              "link": "/text/intro1"}

      return render_template('vid.html', data = data)

    if(part == "intro1"):
      #DO THE INTRO STUFF
      # continue button: 1
      text = "You will be presented with 2 mathematical problems solve. Please solve them to the best of your abilities. Use pen or paper, and the provided tool during your solution. Click 'Continue' to begin"

      data = {"text": text,
              "title": "Intro pt. 1",
              "link": "/experiment/1"}

      return render_template('text.html', data = data)

    if(part == "intro2"):
      #DO THE INTRO STUFF
      # continue button: 3

      text = "You will be presented with 2 mathematical problems solve. Please solve them to the best of your abilities. Use pen or paper, and the provided tool during your solution. Click 'Continue' to begin"

      data = {"text": text,
              "title": "Intro pt. 2",
              "link": "/experiment/3"}

      return render_template('text.html', data = data)

    if(part == "fin"):
      #DO THE INTRO STUFF
      # continue button: 3

      text = "Thank you for taking our study"

      data = {"text": text,
              "title": "Finish",
              "link": "/experiment/fin"}

      return render_template('textNo.html', data = data)

# The equation modifier
@app.route('/experiment/<part>', methods=['POST', 'GET'])
def show_1(part):
    if request.method == 'GET':
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

          data = {"title": title,
                  "link": link_loc}

          return render_template('enterEquation.html', data = data)

    else:
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

        data = {"title": title,
                "link": link_loc}

        # return template
        return render_template('view2.html', state=startState, data = data)


if __name__ == "__main__":
  app.run()
