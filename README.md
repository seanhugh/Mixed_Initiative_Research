## Equation Editing in a Mixed-Initiative User Interface ([Full Paper](https://github.com/seanhugh/Docondo/blob/master/Mixed_Initiative_Interface.pdf) | [Video Demo](https://www.youtube.com/watch?v=3HN2ipgF1Rs))

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) <a href ="https://www.fullstackpython.com/flask.html"><img src="https://github.com/pallets/flask-website/blob/master/flask_website/static/badges/flask-project-s.png" width="100px"></a>
<a href="#"><img src="https://img.shields.io/badge/license-AGPLv3-blue.svg" alt="GitHub license"></a>



#### ABSTRACT
Docondo is a mixed-initiative interface to a computer algebra system enabling user-guided manipulation of algebraic expressions. Simply put, instead of simplifying an equation as much as the computer can instantly and in the manner the computer is programmed to do, it allows the user to guide it step-by-step to achieve the user-desired outcome.

In our research study, we compare this interface to a modified interface that enables fully automatic transformations.

#### Interface Design

The web app runs on python flask. The frontend is lightweight, sending user input to the backend where all calculations are made using modified commands from the numpy library. Equations can be inputted and outputted in Latex at any time to allow for ease of use for the user.

#### Screenshots

1. The user is prompted to input an equation using a latex input package
![Key Result](https://raw.githubusercontent.com/seanhugh/Docondo/master/Images/Input.png)

2. The user is presented with manipulation commands. These allow the user to run operations on the equation, and also move throughout the equation to different subsets.
![Key Result](https://raw.githubusercontent.com/seanhugh/Docondo/master/Images/Manipulate.png)
