var which_active = "1";

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
    return BEGIN.entry.latex();
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
    if(BEGIN.entry.latex()){
      BEGIN.postBegin(window.location.href, { equation: BEGIN.getEquation(), active: $( "#1" ).hasClass( "active" )});
    } else{
      alert("Please enter an equation!")
    }
  });

});


function reply_click(clicked_id)
  {
    if (clicked_id == "1"){
      var active_id = "1";
      var non_active_id = "2";
    } else{
      var active_id = "2";
      var non_active_id = "1";
    }
    which_active = active_id;
    console.log("#" + active_id);
    $( "#" + active_id ).addClass( "active" );
    $( "#" + non_active_id ).removeClass( "active" );
  };
