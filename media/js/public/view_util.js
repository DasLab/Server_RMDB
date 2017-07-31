function open_panel(id) {
    if (id === 'set') {
        $("#set_panel").addClass("visible").animate({"margin-right":"0px"}).css("z-index", "100");
    } else {
        if (id === 'left') {
            $(".panel_close").addClass("visible").show();
            $("#left-buttons").css("margin-top", parseInt($("#left-buttons").css("margin-top")) - parseInt($(".left_close").css("height")));
            $("#left_panel").css("z-index", 100);
            $("#img_panel").css("z-index", 10);
        } else {
            $(".barplot_close").addClass("visible").show();
            $("#img-buttons").css("margin-top", parseInt($("#img-buttons").css("margin-top")) - parseInt($(".left_close").css("height")));
            $("#img_panel").css("z-index", 100);
            $("#left_panel").css("z-index", 10);
        }
        $("#" + id + "_panel").addClass("visible").animate({"margin-left":"0px"}, 500).css("z-index", "100");

        // When overlay shows, disable the "scrolling" of background body.
        document.body.classList.toggle('noscroll', true);
    }
}

function close_panel(id) {
    if (id === 'set') {
        $("#set_panel").removeClass("visible").animate({'margin-right':"-" + $("#set_panel").css("width")}, 500);
    } else {
        if (id === 'left') {
            $(".panel_close").removeClass("visible").hide();
            $("#left-buttons").css("margin-top", parseInt($("#left-buttons").css("margin-top")) + parseInt($(".panel_close").css("height")));
        } else {
            $(".barplot_close").removeClass("visible").hide();
            $("#img-buttons").css("margin-top", parseInt($("#img-buttons").css("margin-top")) + parseInt($(".panel_close").css("height")));
        }
        $("#" + id + "_panel").removeClass("visible").animate({'margin-left':"-" + $("#" + id + "_panel").css("width")}, 500);
        document.body.classList.toggle('noscroll', false);
    }
}


function init_panel_size() {
    $("#left_panel").css("width", Math.max($(window).width() / 2, 600)).css("top", parseInt($(".navbar-fixed-top").css("height"))).css("height", $(window).height() - parseInt($(".navbar-fixed-top").css("height")));
    $(".side_block").css("max-height", parseInt($("#left_panel").css("height")) - 20);
    $("#left-buttons").css("margin-top", parseInt($("#left_panel").css("height")) * 0.8 - parseInt($("#left-buttons").css("height")) - parseInt($(".left_close").css("height")) * 2);

    $("#img_panel").css("width", $(window).width() - 75).css("height", "500px").css("top", $(window).height() - parseInt($("#img_panel").css("height")));
    $("#img-buttons").css("margin-top", parseInt($("#left-buttons").css("height")) + parseInt($("#left-buttons").css("margin-top")) - parseInt($("#img_panel").css("top")) + parseInt($(".navbar-fixed-top").css("height")) - 1);
    $("#svg_parent").css("width", parseInt($("#panel_svg").css("height")) - 90);

    $("#set_panel").css("max-width", "400px").css("width", 300).css("top", parseInt($(".navbar-fixed-top").css("height"))).css("height", $(window).height() - parseInt($(".navbar-fixed-top").css("height")));
}


function render_status(string) {
    var span_class = 'default';
    if (string == 'PUB') {
        string = 'Published';
        span_class = 'success';
    } else if (string == 'HOL') {
        string = 'On Hold';
        span_class = 'danger';
    } else if (string == 'REV') {
        string = 'Under Review';
        span_class = 'warning';
    } else if (string == 'REC') {
        string = 'Received';
        span_class = 'info';
    }
    return '<span class="label label-' + span_class + '">' + string + '</span>';
}

function render_type(string) {
    var span_class = 'default';
    if (string == 'SS' || string == 'DC') {
        string = 'Standard State';
        span_class = 'primary';
    } else if (string == 'MM') {
        string = 'Mutate And Map';
        span_class = 'success';
    } else if (string == 'MR') {
        string = 'Mutation Rescue';
        span_class = 'info';
    } else if (string == 'MA') {
        string = 'MOHCA';
        span_class = 'danger';
    } else if (string == 'TT') {
        string = 'Titration';
        span_class = 'warning';
    }
    return '<span class="label label-' + span_class + '">' + string + '</span>';
}


$(document).ready(function() {
    $(".dropdown-toggle").removeClass("active");
    $("#nav_browse").addClass("active");
    $("#nav_logo").css("text-decoration","none");

    // init_panel_size();
    $(".left_group").on("click", function() { open_panel('left'); });
    $(".panel_close").on("click", function() { close_panel('left'); });
    $(".left_alone").on("click", function() { open_panel('img'); });
    $(".barplot_close").on("click", function() { close_panel('img'); });
    $("#btn-set").on("click", function() {
        if (!$("#set_panel").hasClass("visible")) {
            open_panel('set');
        } else {
            close_panel('set');
        }
    });
    $("#close-set").on("click", function() { close_panel('set'); });

    $("#dl_rdat, #dl_isatab").on("click", function() {$(window).unbind(); });
    $("#show_preview").on("click", function() { $("#preview").modal("show"); });
});


$(window).on("resize", function() {
    clearTimeout($.data(this, 'resizeTimer'));
    $.data(this, 'resizeTimer', setTimeout(function() {
        init_panel_size();
        $("#left_panel").css("margin-left", "-" + $("#left_panel").css("width"));
        $("#img_panel").css("margin-left", "-" + $("#img_panel").css("width"));

        $("#panel_con").css("height", "auto");
        $("#panel_cit").css("height", "auto");
        var col_h = Math.max(parseInt($("#panel_con").css("height")), parseInt($("#panel_cit").css("height")));
        $("#panel_con").css("height", col_h);
        $("#panel_cit").css("height", col_h);

        if ($("#main>svg").width() <= $("div.jumbotron").width()) {
            $("#main").addClass("text-center");
        } else {
            $("#main").removeClass("text-center");
        }
    }, 200));
});


