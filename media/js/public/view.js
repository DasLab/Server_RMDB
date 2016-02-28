$(document).ready(function () {
    if (status === 'PUB') {
        $("#wait").fadeIn();
        $.ajax({
            url: '/site_data/files/' + rmdb_id + '/data_tags.json',
            dataType: 'json',
            async: true,
            success: function(data) {
                tags = data;
                fill_tags();
                init_panel_size();

                setTimeout(function() {
                    if ((tags.data_nrow >= 300 | tags.data_ncol >= 300) & $(location).attr("href").indexOf("?full=1") == -1) {
                        $("#main").html('<p class="text-center lead">Click to <a class="btn btn-danger" id="btn_load_heatmap">Load</a> the Interactive Heatmap ...</p><p class="text-center"><i>(This dataset is large (<code>' + tags.data_nrow + '-by-' + tags.data_ncol + '</code>). Rendering may take a few seconds.)</i></p><img id="img_preview" src="/site_data/construct_img/' + cid + '/reactivity_equal.png" class="center-block well"/>');
                        if (parseInt($("#img_preview").css("width")) > 600) {
                            $("#img_preview").css("width", "600");
                        }
                        $("#btn_load_heatmap").bind("click", function() {
                            $(location).attr("href", $(location).attr("href") + "?full=1");
                        });
                    } else {
                        $.ajax({
                            url: '/site_data/files/' + rmdb_id + '/data_heatmap.json',
                            dataType: 'json',
                            async: false,
                            success: function(data) {
                                json = data;
                                n_rows = json.y_labels.length;
                                draw_heatmap(json);
                            },
                            complete: function(xhr) {
                                $("#svg_top").trigger("click");
                                $("#wait").fadeOut();

                                setTimeout(function() {
                                    init_panel_size();
                                    $("#left_panel").css("margin-left", "0px");
                                    $("#img_panel").css("margin-left", "0px");
                                    $("#set_panel").css("margin-right", "0px");
                                    close_panel('left');
                                    close_panel('img');
                                    close_panel('set');
                                }, 1);
                            }
                        });
                    }
                }, 1);
            }
        });
    } else {
        $("#hist_dropdown").addClass("disabled");
        $("#dl_dropdown").addClass("disabled");
        $("#tag_supercede").html('<button type="button" class="btn btn-warning disabled" data-toggle="dropdown" aria-expanded="false"><span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>&nbsp;&nbsp;In Review&nbsp;&nbsp;</button>');
        var col_h = Math.max(parseInt($("#col-1").css("height")), parseInt($("#col-2").css("height")));
        $("#col-1").css("height", col_h);
        $("#col-2").css("height", col_h);

        init_panel_size();
    }
});
