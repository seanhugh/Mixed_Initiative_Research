  function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
        }
    }

        document.body.appendChild(form);
        form.submit();
    }

$(document).ready(function() {
  window.MATH = {};

  var MQ = MathQuill.getInterface(2);
  //MQ.StaticMath($('#problem')[0]);
  MATH.entry = MQ.MathField($('#entryBox')[0], {
    handlers: {
      edit: function() {
        //checkAnswer(entry.latex());
      }
    }
  });

  MATH.saveEquation = function () {
    entry = MQ.MathField($('#entryBox')[0]);
  }

  // MATH.makePreview = function () {
  //   input = MATH.entry.latex().replace(/</g, "&lt;").replace(/>/g, "&gt;");
  //   $('#preview').html("$$" + input + "$$");
  //   MathJax.Hub.Queue(["Typeset", MathJax.Hub, "preview"]);
  // }

  MATH.makePreview = function () {
    input = MATH.entry.latex().replace(/</g, "&lt;").replace(/>/g, "&gt;");
    input = ("$$" + input + "$$");
    return input
  }

  MATH.showControls = function () {
    MATH.saveEquation();
    // $('#entryWrapper').hide();
    // $('#continueButton').hide();
    //$('#preview').show();
    //$('#controls').show();

    myEq = MATH.makePreview();

    post('/', {equation:  myEq,
               button_clicked: 0,
               tree_loc: 0});

    // window.location.href = '/equation';
  }



  MATH.saveEquation2 = function () {
    entry = MQ.MathField($('#entryBox')[0]);
  }

  MATH.sendData = function () {
    MATH.saveEquation2();
    myEq = MATH.makePreview();

    post('/', {equation:  myEq,
               button_clicked: 0,
               tree_loc: 0});
  }

  // Button Actions

  $('#continueButton').on('click', MATH.showControls);
  $('.action_button').on('click', MATH.sendData);



});
