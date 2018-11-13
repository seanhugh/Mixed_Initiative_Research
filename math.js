$(document).ready(function() {
  window.MATH = {};

  var MQ = MathQuill.getInterface(2);
  MQ.StaticMath($('#problem')[0]);
  var entry = MQ.MathField($('#entryBox')[0], {
    handlers: {
      edit: function() {
        //checkAnswer(entry.latex());
      }
    }
  });

  function saveEquation() {
    entry = MQ.MathField($('#entryBox')[0]);
    console.log(entry.latex());
  }

  function makePreview() {
    input = entry.latex().replace(/</g, "&lt;").replace(/>/g, "&gt;");
    $('#preview').html("$$" + input + "$$");
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, "preview"]);
  }

  function screen2(){
    saveEquation();
    $('#entryWrapper').hide();
    $('#continueButton').hide();
    $('#preview').show();
    $('#controls').show();
    makePreview();
  }

  $('#continueButton').on('click', screen2);
});
