function convertToSlug(Text) {
  return Text.toLowerCase().replace('/', '')
  .replace(/[^a-z0-9-]/g, '-').replace(/\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

function colorRmdbId(string) {
  string = string.split('_');
  s1 = '<span style="color: yellow;">' + string[1] + '</span>';
  s2 = '<span style="color: skyblue;">' + string[2] + '</span>';
  return string[0] + '<span style="color: lightpink;">_</span>' + s1 + '<span style="color: lightpink;">_</span>' + s2;
}

function colorEternaId(string) {
  string = string.split('_');
  s1 = '<span style="color: yellowgreen;">' + string[1] + '</span>';
  s2 = '<span style="color: skyblue;">' + string[2] + '</span>';
  return string[0] + '<span style="color: lightpink;">_</span>' + s1 + '<span style="color: lightpink;">_</span>' + s2;
}

$(document).ready(function() {
  $("#wait").fadeOut(500);
  var today = new Date();
  $("#cp_year").text(today.getFullYear());

  $(".dropdown-toggle").dropdown();
  $(".dropdown").hover(
          function() { $(this).addClass("open"); },
          function() { $(this).removeClass("open"); }
      );
        $("[data-toggle='popover']").popover({trigger: "hover"});
  $("[data-toggle='tooltip']").tooltip();

  $("#top").on("click", function () {
    event.preventDefault();
    $('#top > img').animate({'left':'-5%', 'opacity':'0'}, 125);
    $("html, body").stop().animate({scrollTop: 0}, 250);
  });
  $("#top").hover(
    function(){ $("#top > img").attr("src", "/site_media/images/fg_top.png"); },
    function(){ $("#top > img").attr("src", "/site_media/images/fg_top_hover.png"); }
  );

  $(".clickable").on("click", function() {
    if ($("#buttonAll").length && $(this).attr("id") == "nav_browse") {
      $("#wait").hide();
    } else {
      $("#wait").fadeIn(500);
    }
  });

});

$(window).on("beforeunload", function() {
  $("#wait").fadeIn(500);
});
$(window).on("scroll", function() {
  clearTimeout($.data(this, 'scrollTimer'));
  $.data(this, 'scrollTimer', setTimeout(function() {
    if ($(this).scrollTop() > $(window).height() / 2) {
      $('#top > img').animate({'right':'0%', 'opacity':'1.0'}, 125);
    } else {
      $('#top > img').animate({'right':'-5%', 'opacity':'0'}, 125);
    }
  }, 200));
});

