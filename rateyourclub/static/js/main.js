(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-44445341-1', 'calbeat.com');
ga('send', 'pageview');

var generate_avg_rating_stars = function() {
    avgRating = Math.round(parseFloat($('.avg-rating-val').text()))
    for (var i=0; i < avgRating; i++) {
        $('.avg-rating-stars').append($("<a>").toggleClass("star selected"));
    }
    for (var i=0; i < 5-avgRating; i++) {
        $('.avg-rating-stars').append($("<a>").toggleClass("star"));
    }
}

var generate_review_stars = function() {
    $('.review .rating div').each(function() {
        var rating = $(this).data("rating");
        for (var i=0; i < rating; i++) {
            $(this).append($("<a>").toggleClass("star selected"));
        }
    });
}

var create_review = function() {
    $.post('/reviews/create/', $('#review_form').serialize(), function(response) {
        location.reload();
    }).fail(function(response) {
        msg = JSON.parse(response.responseText)['error'];
        $('#form-errors').text(msg)
        $('#form-errors').show();
    });
}

var getCookie = function(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
