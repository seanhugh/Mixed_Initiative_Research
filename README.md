## Equation Editing in a Mixed-Initiative User Interface ([Full Paper](https://github.com/seanhugh/Docondo/blob/master/Mixed_Initiative_Interface.pdf) | [Video Demo](https://www.youtube.com/watch?v=3HN2ipgF1Rs))

#### ABSTRACT
Docondo is a mixed-initiative interface to a computer algebra system enabling user-guided manipulation of algebraic expressions. Simply put, instead of simplifying an equation as much as the computer can instantly and in the manner the computer is programmed to do, it allows the user to guide it step-by-step to achieve the user-desired outcome.

In our research study, we compare this interface to a modified interface that enables fully automatic transformations.

#### Interface Design

The web app runs on python flask. The frontend is lightweight, sending user input to the backend where all calculations are made using modified commands from the numpy library. Equations can be inputted and outputted in Latex at any time to allow for ease of use for the user.
