$(document).ready(function() {
  window.MATH = {};

  var MQ = MathQuill.getInterface(2);
  MQ.StaticMath($('#problem')[0]);
  MATH.entry = MQ.MathField($('#entryBox')[0], {
    handlers: {
      edit: function() {
        //checkAnswer(entry.latex());
      }
    }
  });

  MATH.saveEquation = function () {
    entry = MQ.MathField($('#entryBox')[0]);
    console.log(entry.latex());
  }

  MATH.makePreview = function () {
    input = MATH.entry.latex().replace(/</g, "&lt;").replace(/>/g, "&gt;");
    $('#preview').html("$$" + input + "$$");
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, "preview"]);
  }

  MATH.showControls = function () {
    MATH.saveEquation();
    $('#entryWrapper').hide();
    $('#continueButton').hide();
    $('#preview').show();
    $('#controls').show();
    MATH.makePreview();
  }

  $('#continueButton').on('click', MATH.showControls);
});
