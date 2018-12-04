$(document).ready(function() {
  window.VIEW = {};

  var MQ = MathQuill.getInterface(2);
  //MQ.StaticMath($('#problem')[0]);
  VIEW.entry = MQ.MathField($('#entryBox')[0], {
    handlers: {
      edit: function() {
        //checkAnswer(entry.latex());
      }
    }
  });

  // update displayed equation
  VIEW.updateEquation = function (equation) {
    // update equation
    $('#equation').html("$$" + equation + "$$");

    // re-render
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, "equation", function () {
      $('#equation').show();
    }]);
  }

  VIEW.makeControlButton = function (txt) {
    return _.template('<div class="controlButton"><%= txt %></div>')({ txt : txt });
  }

  VIEW.updateTreeButtons = function (buttons) {

    if (!VIEW.curState.active) {
      $('#tree_controls').hide();
    }

    possibleButtons = ["up","down","left","right"]

    for (var i = 0; i < possibleButtons.length; i++) {
      var currentButton = possibleButtons[i];
      var className = ("#").concat(currentButton);
        if (buttons.indexOf(currentButton) >= 0) {
            //this button is active
            $(className).removeClass( "inactive" )
        } else{
          $(className).addClass( "inactive" )
        }
    }

  }

  // update displayed controls
  VIEW.updateControls = function (buttons_array) {

    // seperate tree buttons and other buttons
    var buttons = buttons_array[0]
    var tree_buttons = buttons_array[1]

    // Update the tree buttons
    VIEW.updateTreeButtons(tree_buttons);

    // make new buttons
    var newButtons = buttons.map(VIEW.makeControlButton);

    // install new buttons
    $('#controls').empty();
    $('#controls').append(newButtons);

    // install button click handlers
    $('.controlButton').on("click", function (e) {
      name = $(this).text();
      console.log("clicked " + name);

      VIEW.postAction(name, VIEW.update);
    });

    $('#controls').show();
  };

  // update display with given model
  VIEW.update = function (update) {
    // expected format: { equation, buttons, state }
    console.log("got update from server " + update);

    VIEW.curState = update.state;

    $('#equation').hide();
    $('#controls').hide();

    VIEW.updateEquation(update.equation);

    VIEW.updateControls(update.buttons);
  };

  // send action to server
  VIEW.postAction = function (act, callback, method) {
    console.log("posting action " + act);

    method = method || "post"; // Set method to post by default if not specified.

    var xhr = new XMLHttpRequest();   // new HttpRequest instance
    xhr.open("POST", "/update");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.responseType = 'json';
    xhr.onload = function () {
      var status = xhr.status;
      if (status === 200) {
        callback(xhr.response);
      } else {
        console.log("got bad response from server:\n" + xhr.response);
      }
    };

    xhr.send(JSON.stringify({
      "action": act,
      "state": VIEW.curState
    }));
  };

  // send action to server
  VIEW.exportLatex = function () {
    alert(VIEW.curState.equation.raw_eq);
  };

  // update display with initial model
  VIEW.update(window.INIT_STATE);

  // Install button handlers
    $('.treeButton').on("click", function (e) {
      name = $(this).attr('id');
      console.log("clicked " + name);

      VIEW.postAction(name, VIEW.update);
    });

});
