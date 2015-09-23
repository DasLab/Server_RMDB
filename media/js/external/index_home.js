$(document).ready(function() {
  $('.dropdown-toggle').removeClass("active");
  $("#nav_logo>span").css("text-decoration","underline");

  $.ajax({
    url: '/api/index/stats/',
    dataType: 'json',
    async: true,
    success: function(data) {
      $("#N_all").text(data.N_all);
      $("#N_RNA").text(data.N_RNA);
      $("#N_datapoints").text(data.N_datapoints);
      $("#N_constructs").text(data.N_constructs);
    },
    complete: function(xhr) { 
      $.ajax({
        url: '/api/index/latest/',
        dataType: 'json',
        async: true,
        success: function(data) {
          var ind_html = '', body_html = '';
          for (d in data) {
            ind_html += '<li data-target="#carousel-entries" data-slide-to="' + d.toString() + '"></li>';
            body_html += '<div class="item" style="height:300px;"><br/><br/><div class="row"><p class="text-center"><a href="/detail/' + data[d].rmdb_id + '" target="_blank"><span class="label label-default">' + colorRmdbId(data[d].rmdb_id) + '</span><br/>' + data[d].name + '</a></p></div><div class="row"><a href="/detail/' + data[d].rmdb_id + '" target="_blank"><img src="/site_data/thumbs/' + data[d].cid + '.gif" class="center-block"/></a></div></div>';
          }
          $("#slide_index").html(ind_html);
          $("#slide_body").html(body_html);

          $(".carousel-inner>.item:first-child").addClass("active");
          $(".carousel-indicators>li:first-child").addClass("active");
          $('.carousel').carousel();
        },
        complete: function(xhr) {
          $.ajax({
            url: '/api/index/news/',
            dataType: 'json',
            async: true,
            success: function(data) {
              var news_html = '';
              for (d in data) {
                news_html += '<tr><td><i>' + data[d].date + '</i></td><td>' + data[d].title + '</td></tr>';
              }
              $(news_html).insertBefore("#news_table");
            },
            complete: function(xhr) {
              var col_h = Math.max($("#panel_news").height(), $("#panel_slide").height());
              $("#panel_news").css("height", col_h);
              $("#panel_slide").css("height", col_h);

              $("#wait").fadeOut(); 
            }
          });
        }
      });
    }
  });
});