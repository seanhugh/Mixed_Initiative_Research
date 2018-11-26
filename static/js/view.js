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

  // update displayed controls
  VIEW.updateControls = function (buttons) {
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

  // update display with initial model
  VIEW.update(window.INIT_STATE);
});
