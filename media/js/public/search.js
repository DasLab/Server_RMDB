function fill_category(data, tag) {
    var pan_html = '';
    if (tag == "Eterna") {
        pan_html = '<table class="table table-hover table-striped"><thead><tr><th class="col-lg-2 col-md-2 col-sm-3 col-xs-4" style="padding:0px;"></th><th class="col-lg-2 col-md-2 col-sm-3 col-xs-4" style="padding:0px;"></th><th class="col-lg-8 col-md-8 col-sm-6 col-xs-4" style="padding:0px;"></th></tr></thead><tbody>';
        for (var c in data) {
            pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/detail/' + data[c].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Standard State</span></p><i>Version:</i> <mark>' + data[c].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].data_count + '</code></p></td><td id="' + data[c].rmdb_id + '" class="eterna-subpanel"><div style="height:220px;overflow:hidden;"><a href="/detail/' + data[c].rmdb_id + '" class="row browse-rotate thumbnail pull-left" style="left:-300px;"><img src="/site_data/thumbnail/' + data[c].cid + '.gif"/></a></div></td></tr>';
        }
        pan_html += '<tr><td colspan="3" style="padding:0px;"></td></tr>';
    } else {
        pan_html = '<table class="table table-hover table-striped"><thead><tr><th class="col-lg-2 col-md-2 col-sm-3 col-xs-4" style="padding:0px;"></th><th class="col-lg-2 col-md-2 col-sm-3 col-xs-4" style="padding:0px;"></th><th class="col-lg-5 col-md-5 hidden-sm hidden-xs" style="padding:0px;"></th><th class="col-lg-3 col-md-3 col-sm-6 col-xs-4" style="padding:0px;"></th></tr></thead><tbody>';
        for (var c in data) {
            pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/detail/' + data[c].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Standard State</span></p><i>Version:</i> <mark>' + data[c].version + '</mark><br/><i># of Construct:</i> <code>'+ data[c].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].data_count + '</code></p></td><td class="hidden-sm hidden-xs"><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].authors + '</i>. <b>' + data[c].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].comments + '</p></td><td><a href="/detail/' + data[c].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbnail/' + data[c].cid + '.gif" width="100%"/></a></td></tr>';
        }
        pan_html += '<tr><td colspan="4" style="padding:0px;"></td></tr>';
    }
    pan_html += '</tbody></table>';
    return pan_html;
}

function render_nomatch() {
    $("#categoryGeneral").css("display", "none");
    $("#categoryEterna").css("display", "none");
    $("#categoryNA").css("display", "inline");
}


$(document).ready(function() {
    $(".dropdown-toggle").removeClass("active");
    $("#nav_browse").addClass("active");
    $("#nav_logo").css("text-decoration","none");

    $("#buttonGeneral, #buttonEterna").on("click", function () {
        $('html, body').stop().animate({scrollTop: $($(this).attr("href")).offset().top - 75}, 500);
    });


    $.ajax({
        url: '/get_stats/',
        dataType: 'json',
        async: true,
        success: function(data) {
            $("#N_all").text(data.N_all);
        }
    });

    var search_word = $("#sstring").text();
    if (search_word) {
        $.ajax({
            url: '/api/search/' + search_word + '?type=general',
            dataType: 'json',
            async: true,
            success: function(data) {
                $("#panel_general").removeClass('place_holder').html(fill_category(data, 'General'));
                if (data.length) {
                    $("#N_search").html('<a id="buttonGeneral" href="#categoryGeneral" style="color:inherit"><span class="glyphicon glyphicon-heart" aria-hidden="true"></span>&nbsp;General # Entries</a>: <span class="badge" >' + data.length + '</span><br/>');
                }
            }
        });
        $.ajax({
            url: '/api/search/' + search_word + '?type=eterna',
            dataType: 'json',
            async: true,
            success: function(data) {
                $("#panel_eterna").removeClass('place_holder').html(fill_category(data, 'Eterna'));
                if (data.length) {
                    $("#N_search").html($("#N_search").html() + '<a id="buttonEterna" href="#categoryEterna" style="color:inherit"><span class="glyphicon glyphicon-cloud" aria-hidden="true"></span>&nbsp;Eterna # Entries</a>: <span class="badge" >' + data.length + '</span><br/>');
                }
            },
            complete: function(xhr) {
                if(!$("#N_search").html().length) {
                    render_nomatch();
                }
            }
        });
    } else {
        render_nomatch();
    }
});

