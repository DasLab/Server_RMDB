$(document).ready(function() {
  $('.dropdown-toggle').removeClass("active");
  $("#nav_about").addClass("active");
  $("#nav_logo").css("text-decoration","none");

  $(".clickable").on("click", function() {
    var click_id = $(this).attr("id");
    if ( click_id == "nav_contact" | click_id == "nav_cite") {
      $("#wait").hide();
    }
  });

  $("#logo").on("click", function(e) {
    e.preventDefault();
    $("#show_logo").modal("show");
  });

  $.ajax({
    url: '/get_stats/',
    dataType: 'json',
    async: true,
    success: function(data) {
      $("#N_all").text(data.N_all);
      $("#N_RNA").text(data.N_RNA);
      $("#N_datapoints").text(data.N_datapoints);
      $("#N_constructs").text(data.N_constructs);
    }
  });
});


