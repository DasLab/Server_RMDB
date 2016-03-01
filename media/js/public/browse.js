var json_general, json_puzzle, json_eterna;

function fill_category(data, tag, view) {
    var pan_html = '';
    for (var c in data) {
        if (tag == "Eterna") {
            if (view == 'list') {
                pan_html = '<table class="table table-hover table-striped"><thead><tr><th class="col-lg-2 col-md-2 col-sm-3 col-xs-4" style="padding:0px;"></th><th class="col-lg-2 col-md-2 col-sm-3 col-xs-4" style="padding:0px;"></th><th class="col-lg-8 col-md-8 col-sm-6 col-xs-4" style="padding:0px;"></th></tr></thead><tbody>';
                for (var e in data[c].SS_entry) {
                    pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/detail/' + data[c].SS_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].SS_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Standard State</span></p><i>Version:</i> <mark>' + data[c].SS_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].SS_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].SS_entry[e].data_count + '</code></p></td><td id="' + data[c].SS_entry[e].rmdb_id + '" class="eterna-subpanel"><div style="height:220px;overflow:hidden;"><a href="/detail/' + data[c].SS_entry[e].rmdb_id + '" class="row browse-rotate thumbnail pull-left" style="left:-300px;"><img src="/site_data/thumbnail/' + data[c].SS_entry[e].rmdb_id + '.gif"/></a></div></td></tr>';
                }
                pan_html += '<tr><td colspan="3" style="padding:0px;"></td></tr></tbody></table>';
            } else {
                for (var e in data[c].SS_entry) {
                    pan_html += '<div class="panel panel-default subpanel eterna-panel"><div id="heading' + convertToSlug(data[c].SS_entry[e].rmdb_id) + '" class="panel-heading" role="tab" data-toggle="collapse" data-parent="#category' + tag + '" href="#' + convertToSlug(data[c].SS_entry[e].rmdb_id) + '" aria-expanded="true" aria-controls="' + convertToSlug(data[c].SS_entry[e].rmdb_id) + '"><div class="panel-title" ><span class="icon glyphicon glyphicon-chevron-right" aria-hidden="true"></span>&nbsp;&nbsp;<span class="label label-default" style="font-size:16px;">' + colorEternaId(data[c].SS_entry[e].rmdb_id) + '</span></div></div><div id="'+ convertToSlug(data[c].SS_entry[e].rmdb_id) + '" class="panel-collapse collapse eterna-subpanel" role="tabpanel" aria-labelledby="heading'+ convertToSlug(data[c].SS_entry[e].rmdb_id) + '"><div class="panel-body"><a href="/detail/'+ data[c].SS_entry[e].rmdb_id + '" class="row browse-rotate thumbnail pull-left" style="left:-200px;"><img src="/site_data/thumbnail/' + data[c].SS_entry[e].rmdb_id + '.gif"/></a><br/></div></div></div>';
                }
            }
        } else {
            if (view == 'list') {
                pan_html += '<div class="panel panel-default subpanel"><div id="heading' + convertToSlug(data[c].name) + '" class="panel-heading" role="tab" data-toggle="collapse" data-parent="#category' + tag + '" href="#' + convertToSlug(data[c].name) + '" aria-expanded="true" aria-controls="' + convertToSlug(data[c].name) + '"><h3 class="panel-title"><span class="icon glyphicon glyphicon-chevron-right" aria-hidden="true"></span>&nbsp;&nbsp;<span>' + data[c].name + '</span></h3></div><div id="' + convertToSlug(data[c].name) + '" class="panel-collapse collapse" role="tabpanel" aria-labelledby="heading' + convertToSlug(data[c].name) + '"><div class="panel-body"><table class="table table-hover table-striped"><thead><tr><th class="col-lg-2 col-md-2 col-sm-3 col-xs-4" style="padding:0px;"></th><th class="col-lg-2 col-md-2 col-sm-3 col-xs-4" style="padding:0px;"></th><th class="col-lg-5 col-md-5 hidden-sm hidden-xs" style="padding:0px;"></th><th class="col-lg-3 col-md-3 col-sm-6 col-xs-4" style="padding:0px;"></th></tr></thead><tbody>';

            } else {
                pan_html += '<div class="panel panel-default subpanel"><div id="heading' + convertToSlug(data[c].name) + '" class="panel-heading" role="tab" data-toggle="collapse" data-parent="#category' + tag + '" href="#' + convertToSlug(data[c].name) + '" aria-expanded="true" aria-controls="' + convertToSlug(data[c].name) + '"><h3 class="panel-title"><span class="icon glyphicon glyphicon-chevron-right" aria-hidden="true"></span>&nbsp;&nbsp;<span>' + data[c].name + '</span></h3></div><div id="' + convertToSlug(data[c].name) + '" class="panel-collapse collapse" role="tabpanel" aria-labelledby="heading' + convertToSlug(data[c].name) + '"><div class="panel-body"><ul>';

            }

            if (data[c].SS_entry.length) {
                if (view == 'list') {
                    for (var e in data[c].SS_entry) {
                        pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/detail/' + data[c].SS_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].SS_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Standard State</span></p><i>Version:</i> <mark>' + data[c].SS_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].SS_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].SS_entry[e].data_count + '</code></p></td><td class="hidden-sm hidden-xs"><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].SS_entry[e].authors + '</i>. <b>' + data[c].SS_entry[e].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].SS_entry[e].comments + '</p></td><td><a href="/detail/' + data[c].SS_entry[e].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbnail/' + data[c].SS_entry[e].rmdb_id + '.gif" width="100%"/></a><br/></td></tr>';
                    }
                } else {
                    pan_html += '<li><h3><span class="label label-primary">Standard State</span></h3></li><div class="row">';
                    for (var e in data[c].SS_entry) {
                        pan_html += '<div class="col-lg-4 col-md-4 col-sm-6 col-xs-12 entry-list"><a href="/detail/' + data[c].SS_entry[e].rmdb_id + '" class="thumbnail"><p class="lead" style="padding-top:10px;"><span class="label label-default">' + colorRmdbId(data[c].SS_entry[e].rmdb_id) + '</span></p><img src="/site_data/thumbnail/' + data[c].SS_entry[e].rmdb_id + '.gif"/><br/></a></div>';
                    }
                    pan_html += '</div>';
                }
            }
            if (data[c].TT_entry.length) {
                if (view == 'list') {
                    for (var e in data[c].TT_entry) {
                        pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/detail/' + data[c].TT_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].TT_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Titration</span></p><i>Version:</i> <mark>' + data[c].TT_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].TT_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].TT_entry[e].data_count + '</code></p></td><td class="hidden-sm hidden-xs"><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].TT_entry[e].authors + '</i>. <b>' + data[c].TT_entry[e].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].TT_entry[e].comments + '</p></td><td><a href="/detail/' + data[c].TT_entry[e].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbnail/' + data[c].TT_entry[e].rmdb_id + '.gif"/></a><br/></td></tr>';
                    }
                } else {
                    pan_html += '<li><h3><span class="label label-info">Titration</span></h3></li><div class="row">';
                    for (var e in data[c].TT_entry) {
                        pan_html += '<div class="col-lg-4 col-md-4 col-sm-6 col-xs-12 entry-list"><a href="/detail/' + data[c].TT_entry[e].rmdb_id + '" class="thumbnail"><p class="lead" style="padding-top:10px;"><span class="label label-default">' + colorRmdbId(data[c].TT_entry[e].rmdb_id) + '</span></p><img src="/site_data/thumbnail/' + data[c].TT_entry[e].rmdb_id + '.gif" width="100%"/><br/></a></div>';
                    }
                    pan_html += '</div>';
                }
            }
            if (data[c].MM_entry.length) {
                if (view == 'list') {
                    for (var e in data[c].MM_entry) {
                        pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/detail/' + data[c].MM_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].MM_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Mutate and Map</span></p><i>Version:</i> <mark>' + data[c].MM_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].MM_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].MM_entry[e].data_count + '</code></p></td><td class="hidden-sm hidden-xs"><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].MM_entry[e].authors + '</i>. <b>' + data[c].MM_entry[e].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].MM_entry[e].comments + '</p></td><td><a href="/detail/' + data[c].MM_entry[e].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbnail/' + data[c].MM_entry[e].rmdb_id + '.gif" width="100%"/></a><br/></td></tr>';
                    }
                } else {
                    pan_html += '<li><h3><span class="label label-success">Mutate and Map</span></h3></li><div class="row">';
                    for (var e in data[c].MM_entry) {
                        pan_html += '<div class="col-lg-4 col-md-4 col-sm-6 col-xs-12 entry-list"><a href="/detail/' + data[c].MM_entry[e].rmdb_id + '" class="thumbnail"><p class="lead" style="padding-top:10px;"><span class="label label-default">' + colorRmdbId(data[c].MM_entry[e].rmdb_id) + '</span></p><img src="/site_data/thumbnail/' + data[c].MM_entry[e].rmdb_id + '.gif"/><br/></a></div>';
                    }
                    pan_html += '</div>';
                }
            }
            if (data[c].MA_entry.length) {
                if (view == 'list') {
                    for (var e in data[c].MA_entry) {
                        pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/detail/' + data[c].MA_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].MA_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">MOHCA</span></p><i>Version:</i> <mark>' + data[c].MA_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].MA_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].MA_entry[e].data_count + '</code></p></td><td class="hidden-sm hidden-xs"><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].MA_entry[e].authors + '</i>. <b>' + data[c].MA_entry[e].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].MA_entry[e].comments + '</p></td><td><a href="/detail/' + data[c].MA_entry[e].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbnail/' + data[c].MA_entry[e].rmdb_id + '.gif" width="100%"/></a><br/></td></tr>';
                    }
                } else {
                    pan_html += '<li><h3><span class="label label-danger">MOHCA</span></h3></li><div class="row">';
                    for (var e in data[c].MA_entry) {
                        pan_html += '<div class="col-lg-4 col-md-4 col-sm-6 col-xs-12 entry-list"><a href="/detail/' + data[c].MA_entry[e].rmdb_id + '" class="thumbnail"><p class="lead" style="padding-top:10px;"><span class="label label-default">' + colorRmdbId(data[c].MA_entry[e].rmdb_id) + '</span></p><img src="/site_data/thumbnail/' + data[c].MA_entry[e].rmdb_id + '.gif"/><br/></a></div>';
                    }
                    pan_html += '</div>';
                }
            }

            if (view == 'list') {
                pan_html += '<tr><td colspan="4" style="padding:0px;"></td></tr></tbody></table></div></div></div>';
            } else {
                pan_html += '</ul></div></div></div>';
            }
        }
    }
    return pan_html;
}


function bind_panel_collapse() {
    $('.panel-collapse').on('show.bs.collapse', function() {
        $(this).siblings().find(".panel-title > .icon").removeClass("glyphicon-chevron-right").addClass("glyphicon-chevron-down");
    });
    $('.panel-collapse').on('hidden.bs.collapse', function() {
        $(this).siblings().find(".panel-title > .icon").removeClass("glyphicon-chevron-down").addClass("glyphicon-chevron-right");
    });

}


$(document).ready(function() {
    $(".dropdown-toggle").removeClass("active");
    $("#nav_browse").addClass("active");
    $("#nav_logo").css("text-decoration","none");

    $.ajax({
        url: '/get_stats/',
        dataType: 'json',
        async: true,
        success: function(data) {
            $("#N_all").text(data.N_all);
            $("#N_general").text(data.N_all - data.N_puzzle - data.N_eterna);
            $("#N_puzzle").text(data.N_puzzle);
            $("#N_eterna").text(data.N_eterna);
        }
    });

    $.ajax({
        url: '/get_browse/general/',
        dataType: 'json',
        async: true,
        success: function(data) {
            json_general = data;
            $("#panel_general").removeClass('place_holder').html(fill_category(json_general, 'General', 'thumb'));
            $("#categoryGeneral").find(".panel-body > .subpanel:first > .panel-collapse").collapse("show");
            $("#categoryGeneral").find(".panel-body > .subpanel:first > .panel-collapse").siblings().find(".panel-title > .icon").removeClass("glyphicon-chevron-right").addClass("glyphicon-chevron-down");
        }
    });
    $.ajax({
        url: '/get_browse/puzzle/',
        dataType: 'json',
        async: true,
        success: function(data) {
            json_puzzle = data;
            $("#panel_puzzle").removeClass('place_holder').html(fill_category(json_puzzle, 'Puzzle', 'thumb'));
            $("#categoryPuzzle").find(".panel-body > .subpanel:first > .panel-collapse").collapse("show");
            $("#categoryPuzzle").find(".panel-body > .subpanel:first > .panel-collapse").siblings().find(".panel-title > .icon").removeClass("glyphicon-chevron-right").addClass("glyphicon-chevron-down");
        }
    });
    $.ajax({
        url: '/get_browse/eterna/',
        dataType: 'json',
        async: true,
        success: function(data) {
            json_eterna = data;
            $("#panel_eterna").removeClass('place_holder').html(fill_category(json_eterna, 'Eterna', 'thumb'));
            $("#categoryEterna").find(".panel-body > .subpanel:first > .panel-collapse").collapse("show");
            $("#categoryEterna").find(".panel-body > .subpanel:first > .panel-collapse").siblings().find(".panel-title > .icon").removeClass("glyphicon-chevron-right").addClass("glyphicon-chevron-down");
        }
    });

    setTimeout(bind_panel_collapse, 50);


    $("#buttonAll, #buttonGeneral, #buttonPuzzle, #buttonEterna").on("click", function() {
        $("#categoryGeneral, #categoryPuzzle, #categoryEterna").hide();
        $("#buttonAll, #buttonGeneral, #buttonPuzzle, #buttonEterna").removeClass("active");
    });
    $("#buttonAll").on("click", function() {
        $("#categoryGeneral, #categoryPuzzle, #categoryEterna").show();
        $("#buttonAll").addClass("active");
        $('html, body').stop().animate({scrollTop: 0}, 500);
    });
    $("#buttonGeneral").on("click", function() {
        $("#categoryGeneral").show();
        $("#buttonGeneral").addClass("active");
        $('html, body').stop().animate({scrollTop: 0}, 500);
    });
    $("#buttonPuzzle").on("click", function() {
        $("#categoryPuzzle").show();
        $("#buttonPuzzle").addClass("active");
        $('html, body').stop().animate({scrollTop: 0}, 500);
    });
    $("#buttonEterna").on("click", function() {
        $("#categoryEterna").show();
        $("#buttonEterna").addClass("active");
        $('html, body').stop().animate({scrollTop: 0}, 500);
    });

    $("input:radio").on("change", function() {
        if ($(this).val() == "thumb") {
            $("#panel_general").addClass('place_holder').html(fill_category(json_general, 'General', 'thumb')).removeClass('place_holder');
            $("#panel_puzzle").addClass('place_holder').html(fill_category(json_puzzle, 'Puzzle', 'thumb')).removeClass('place_holder');
            $("#panel_eterna").addClass('place_holder').html(fill_category(json_eterna, 'Eterna', 'thumb')).removeClass('place_holder');
        } else {
            $("#panel_general").addClass('place_holder').html(fill_category(json_general, 'General', 'list')).removeClass('place_holder');
            $("#panel_puzzle").addClass('place_holder').html(fill_category(json_puzzle, 'Puzzle', 'list')).removeClass('place_holder');
            $("#panel_eterna").addClass('place_holder').html(fill_category(json_eterna, 'Eterna', 'list')).removeClass('place_holder');
        }

        $(".category").each(function() {
            $(this).find(".panel-body > .subpanel:first > .panel-collapse").collapse("show");
        });
        bind_panel_collapse();
    });

    $('#expand_all').on("click", function() {
        $(".category").each(function() {
            $(this).find(".panel-body > .subpanel > .panel-collapse").collapse("show");
        });
    });
    $('#collapse_all').on("click", function() {
        $(".category").each(function() {
            $(this).find(".panel-body > .subpanel > .panel-collapse").collapse("hide");
        });
    });


});