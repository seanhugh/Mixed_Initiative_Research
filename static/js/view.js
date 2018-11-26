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
  VIEW.updateEquation = function (model) {
    // update equation
    var eq = model.equation;
    $('#equation').html("$$" + eq + "$$");

    // re-render
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, "equation", function () {
      $('#equation').show();
    }]);
  }

  VIEW.makeControlButton = function (txt) {
    return _.template('<div class="controlButton"><%= txt %></div>')({ txt : txt });
  }

  // install button click handlers
  VIEW.installControlButtonHandlers = function () {
    $('.controlButton').on("click", function (e) {
      name = $(this).text();
      console.log("clicked " + name);

      VIEW.postAction(name, VIEW.update);
    });
  };

  // update displayed controls
  VIEW.updateControls = function (model) {
    // make new buttons
    var newButtons = [];
    newButtons.push(VIEW.makeControlButton('divide'));
    newButtons.push(VIEW.makeControlButton('factor'));
    newButtons.push(VIEW.makeControlButton('multiply'));

    // install new buttons
    $('#controls').empty();
    $('#controls').append(newButtons);
    VIEW.installControlButtonHandlers();

    $('#controls').show();
  };

  // update display with given model
  VIEW.update = function (model) {
    console.log(model);

    $('#equation').hide();
    $('#controls').hide();

    VIEW.updateEquation(model);
    VIEW.updateControls(model);
  };

  // send action to server
  VIEW.postAction = function (params, callback, method) {
    console.log("posting " + params);

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
        alert("fail");
      }
    };

    xhr.send(JSON.stringify({ "email": "hello@user.com",
                              "action": params,
                              "response": { "name": "Tester" } }));
  };

  // update display with initial model
  VIEW.update(window.INIT_MODEL);
});
