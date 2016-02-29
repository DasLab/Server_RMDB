$(document).ready(function () {
    if (status === 'PUB') {
        $("#wait").fadeIn();
        $.ajax({
            url: '/site_data/json/' + rmdb_id + '-tags.json',
            dataType: 'json',
            async: true,
            success: function(data) {
                tags = data;
                fill_tags();
                init_panel_size();

                setTimeout(function() {
                    if ((tags.data_nrow >= 300 | tags.data_ncol >= 300) & $(location).attr("href").indexOf("?full=1") == -1) {
                        $("#main").html('<p class="text-center lead">Click to <a class="btn btn-danger" id="btn_load_heatmap"><span class="glyphicon glyphicon-hourglass"></span>&nbsp;&nbsp;Load&nbsp;</a> the Interactive Heatmap ...</p><p class="text-center"><i>(This dataset is large (<code>' + tags.data_nrow + '-by-' + tags.data_ncol + '</code>). Rendering may take a few seconds.)</i></p><img id="img_preview" src="/site_data/image/' + cid + '/reactivity_crisp.png" class="center-block well"/>');
                        if (parseInt($("#img_preview").css("width")) > 600) {
                            $("#img_preview").css("width", "600px");
                        }
                        $("#btn_load_heatmap").bind("click", function() {
                            $(location).attr("href", $(location).attr("href") + "?full=1");
                        });

                        setTimeout(function() {
                            init_panel_size();
                            $("#left_panel").css("margin-left", "0px");
                            $("#img_panel").css("margin-left", "0px");
                            $("#set_panel").css("margin-right", "0px");
                            close_panel('left');
                            close_panel('img');
                            close_panel('set');
                        }, 1);
                        $("#wait").fadeOut();
                    } else {
                        $.ajax({
                            url: '/site_data/json/' + rmdb_id + '-hmap.json',
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
        $("#header_stat").html(render_status(status));
        $("#hist_dropdown").addClass("disabled");
        $("#dl_dropdown").addClass("disabled");
        $("#tag_supercede").html('<button type="button" class="btn btn-warning disabled" data-toggle="dropdown" aria-expanded="false"><span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>&nbsp;&nbsp;Under Review&nbsp;</button>');

        $("#img_prv_rev").attr("src", "/site_data/image/" + cid + "/reactivity_crisp.png");
        $("#dl_isatab_rev").attr("href", "/site_data/file/" + rmdb_id + "/" + rmdb_id + "_" + version + ".xls");
        $("#dl_rdat_rev").attr("href", "/site_data/file/" + rmdb_id + "/" + rmdb_id + ".rdat");

        var col_h = Math.max(parseInt($("#col-1").css("height")), parseInt($("#col-2").css("height")));
        $("#col-1").css("height", col_h);
        $("#col-2").css("height", col_h);

        $("#left_panel, img_panel, set_panel").hide();
    }
});
