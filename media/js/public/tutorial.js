function resize() {
  $("#main").addClass("pull-right");
  $("#sidebar").css("width", $("#nav_load").width() - $("#main").width() - 30);

  if ($("#sidebar").width() < 200) {
    degree = 1;
    $("#side").removeClass("col-lg-2 col-md-2").addClass("row");
    $("#main").addClass("row").removeClass("pull-right");
    $("#sidebar").css("width", "auto").removeAttr("data-spy").removeClass("affix").removeClass("affix-top");
    $("#side_con").addClass("container");
  } else {
    $("#side").addClass("col-lg-2 col-md-2").removeClass("row");
    $("#main").removeClass("row").addClass("pull-right");
    $("#sidebar").attr("data-spy","affix").affix( { offset: { top: $("#main").position().top } } );
    $("#side_con").removeClass("container");

    if ($("#nav_load").width() >= 1680) {
      $("#sidebar").css("width", ($("#nav_load").width() - $("#main").width())/2 -25);
      $("#main").removeClass("pull-right").addClass("row");
      degree = 3;
    } else {
      $("#main").addClass("pull-right");
      $("#sidebar").css("width", ($("#nav_load").width() - $("#main").width()) -25);
      degree = 2;
    }
  }
}

var degree = 0;

$(document).ready(function () {
  resize();

  $('body').scrollspy({
    'target': '.scroll_nav',
    'offset': 150
  });
  $('.scroll_nav').on('activate.bs.scrollspy', function () {
    $('.scroll_nav > ul > li:not(.active) > ul.panel-collapse').collapse('hide');
    $('.scroll_nav > ul > li.active > ul.panel-collapse').collapse('show');
  });

  $('[id^=tab_], #up').on('click', function () {
    $('html, body').stop().animate({scrollTop: $($(this).attr("href")).offset().top - 75}, 500);
  });

  $('ul.panel-collapse').on('show.bs.collapse', function () {
    $(this).parent().find("a>span.glyphicon.pull-right")
      .removeClass("glyphicon-triangle-bottom")
      .addClass("glyphicon-triangle-top");
  });
  $('ul.panel-collapse').on('hide.bs.collapse', function () {
    $(this).parent().find("a>span.glyphicon.pull-right")
      .removeClass("glyphicon-triangle-top")
      .addClass("glyphicon-triangle-bottom");
  });

});

$(window).on("scroll", function () {
  if (degree == 1) {
    $("#sidebar").css("width", "auto").removeAttr("data-spy").removeClass("affix").removeClass("affix-top");
  }
});

$(window).on("resize", function() {
  clearTimeout($.data(this, 'resizeTimer'));
  $.data(this, 'resizeTimer', setTimeout(resize, 200));
});

