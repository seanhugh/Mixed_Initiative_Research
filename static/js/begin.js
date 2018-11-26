$(document).ready(function() {
  window.BEGIN = {};

  var MQ = MathQuill.getInterface(2);
  BEGIN.entry = MQ.MathField($('#entryBox')[0], {
    handlers: {
      edit: function() {
        //checkAnswer(entry.latex());
      }
    }
  });

  // get equation as latex
  BEGIN.getEquation = function () {
    return BEGIN.entry.latex().replace(/</g, "&lt;").replace(/>/g, "&gt;");
  };

  // fetch next page
  BEGIN.postBegin = function (path, params, method) {
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
  };

  // post equation to server to start interaction
  $('#beginButton').on('click', function () {
    BEGIN.postBegin('/', { equation: BEGIN.getEquation() });
  });
});
