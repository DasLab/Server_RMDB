var $ = django.jQuery;

function replace_path(string) {
    return string.replace('/home/ubuntu/Server_Primerize/data/', '/site_data/').replace('/Website_Server/Primerize/data/', '/site_data/');
}

function render_status(string) {
    var span_class = 'default';
    if (string == 'Success') {
        span_class = 'success';
    } else if (string == 'Error') {
        span_class = 'danger';
    } else if (string == 'Underway') {
        span_class = 'warning';
    } else if (string == 'Fail') {
        span_class = 'orange';
    } else if (string == 'Demo') {
        span_class = 'info';
    }
    return '<span class="label label-' + span_class + '">' + string + '</span>';
}

function render_type(string) {
    var span_class = 'default';
    if (string == 'Simple Assembly') {
        span_class = 'primary';
    } else if (string == 'Mutate-and-Map') {
        span_class = 'orange';
    } else if (string == 'Mutation/Rescue') {
        span_class = 'teal';
    }
    return '<span class="label label-' + span_class + '">' + string + '</span>';
}

$(document).ready(function () {
    // $('script[src="/static/admin/js/admin/DateTimeShortcuts.js"]').remove();
    // $('script[src="/static/admin/js/jquery.js"]').remove();
    // $('script[src="/static/admin/js/jquery.init.js"]').remove();

    $("label.required").css("font-weight", "bold");
    $("table").addClass("table-hover").removeClass("table-bordered table-condensed");
    $('[scope="col"]').addClass("info");

    $("a.deletelink").css("box-sizing", "border-box");
    $("input").addClass("form-control");
    $("select").addClass("form-control");
    $("textarea").addClass("form-control");
    $("#id_sequence, #id_primers, #id_params, #id_plates").addClass("monospace");
    $("#id_job_id, #id_job_1d, #id_job_2d, #id_job_3d").addClass("monospace job_id");
    $("span.add-on").html('<span class="glyphicon glyphicon-calendar"></span>').addClass("input-group-addon").removeClass("add-on");

    $('th > div.text > span > input[type="checkbox"]').each(function() {
        var parent = $(this).parent();
        $(this).css("display", "");
        $(this).detach().insertBefore(parent);
    });
    $('input[type="checkbox"], input[type="radio"]').each(function() {
        if ($(this).next().is("label")) {
            $(this).parent().addClass("checkbox");
            $(this).prependTo($(this).next());
        } else {
            $(this).removeClass("form-control");
            $(this).next().css("padding-left", "10px");
            $('<label></label>').insertBefore($(this));
            var elem = $(this).prev();
            $(this).next().appendTo(elem);
            $('<span class="cr"><span class="cr-icon glyphicon glyphicon-ok"></span></span>').prependTo(elem);
            $(this).prependTo(elem);
            $('<div class="checkbox"></div>').insertBefore(elem);
            elem.appendTo(elem.prev());
        }
    });
    
    $('p.file-upload > a').each(function() {
        $(this).replaceWith('<div class="form-inline"><label>Current:&nbsp;&nbsp;</label><input class="form-control" disabled="disabled" style="cursor:text;" value="' + $(this).attr("href") + '">&nbsp;&nbsp;<a href="'+ replace_path($(this).attr("href")) + '" class="btn btn-default" target="_blank"><span class="glyphicon glyphicon-cloud-download"></span>&nbsp;&nbsp;View&nbsp;&nbsp;</a></div>');
    });
    $('.clearable-file-input').each(function() {
        $(this).appendTo($(this).prev());
        $(this).children().contents().filter(function () {return this.data === "Clear";}).replaceWith("&nbsp;&nbsp;<span class='glyphicon glyphicon-remove-sign'></span>&nbsp;Clear");
    });
    $('input[type="file"]').each(function() {
        $('<div class="form-inline"><label>Change:&nbsp;&nbsp;</label><input id="' + $(this).attr("id") + '_disp" class="form-control" placeholder="No file chosen" disabled="disabled" style="cursor:text;"/>&nbsp;&nbsp;<div id="' + $(this).attr("id") + '_btn" class="fileUpload btn btn-info"><span><span class="glyphicon glyphicon-folder-open"></span>&nbsp;&nbsp;Browse&nbsp;&nbsp;</span></div>').insertAfter(this);
        $(this).detach().appendTo('#' + $(this).attr("id") + '_btn');

        $(this).on("change", function () {
            $('#' + $(this).attr("id") + '_disp').val($(this).val().replace("C:\\fakepath\\", ""));
        });
        $('.file-upload').contents().filter(function () {return this.data === "Change: " | this.data === "Currently: ";}).remove();
    });
    $('input[disabled="disabled"]').each(function() {
        $(this).width($(this).width()*2.5);
    });

    $(".toggle.descending").html('<span class="glyphicon glyphicon-chevron-up"></span>');
    $(".toggle.ascending").html('<span class="glyphicon glyphicon-chevron-down"></span>');
    $(".sortremove").html('<span class="glyphicon glyphicon-remove"></span>');
    $(".sortoptions").addClass("pull-right").removeClass("sortoptions");
    $("div.pagination-info").html("<br/>&nbsp;&nbsp;&nbsp;&nbsp;" + $("div.pagination-info").html());

    if ($(location).attr("href").indexOf("admin/src/jobids") != -1) {
        $("th.column-date").addClass("col-lg-3 col-md-3 col-sm-3 col-xs-3");
        $("th.column-job_id").addClass("col-lg-6 col-md-6 col-sm-6 col-xs-6");
        $("th.column-type").addClass("col-lg-3 col-md-3 col-sm-3 col-xs-3");

        $("td.field-job_id").each(function() { $(this).html("<kbd>" + $(this).html() + "</kbd>"); });
        $("td.field-type").each(function() { $(this).html(render_type($(this).html())); });

        $("th.column-job_id > div.text > a").html('<span class="glyphicon glyphicon-credit-card"></span>&nbsp;&nbsp;Job IDs');
        $("th.column-type > div.text > a").html('<span class="glyphicon glyphicon-adjust"></span>&nbsp;&nbsp;Job Type');

        $("div.col-md-6 > h2.legend").html('<span class="glyphicon glyphicon-credit-card"></span>&nbsp;' + $("div.col-md-6 > h2.legend").html() + '<span class="pull-right" style="font-weight:normal; font-size: 12px;">(Click values in first column to edit)</span>');
        $("ul.breadcrumb > li:first").next().remove();
        $("ul.breadcrumb > li:first").next().prepend('<span style="color: #000;" class="glyphicon glyphicon-credit-card"></span>&nbsp;&nbsp;');
    } else if ($(location).attr("href").indexOf("admin/src/jobgroups") != -1) {
        $("th.column-id").addClass("col-lg-1 col-md-1 col-sm-1 col-xs-1");
        $("th.column-tag").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-job_1d").addClass("col-lg-3 col-md-3 col-sm-3 col-xs-3");
        $("th.column-job_2d").addClass("col-lg-3 col-md-3 col-sm-3 col-xs-3");
        $("th.column-job_3d").addClass("col-lg-3 col-md-3 col-sm-3 col-xs-3");

        $("td.field-tag").css("font-style", "italic");
        $("td.field-job_1d").each(function() { $(this).html("<kbd>" + $(this).html() + "</kbd>"); });
        $("td.field-job_2d").each(function() { $(this).html("<kbd>" + $(this).html() + "</kbd>"); });
        $("td.field-job_3d").each(function() { $(this).html("<kbd>" + $(this).html() + "</kbd>"); });

        $("th.column-id > div.text > a").html('<span class="glyphicon glyphicon-th-large"></span>');
        $("th.column-tag > div.text > a").html('<span class="glyphicon glyphicon-tag"></span>&nbsp;&nbsp;Job Tag');
        $("th.column-job_1d > div.text > a").html('<span class="glyphicon glyphicon-credit-card"></span>&nbsp;&nbsp;Job Entry of <code>Design1D</code>');
        $("th.column-job_2d > div.text > a").html('<span class="glyphicon glyphicon-credit-card"></span>&nbsp;&nbsp;Job Entry of <code>Design2D</code>');
        $("th.column-job_3d > div.text > a").html('<span class="glyphicon glyphicon-credit-card"></span>&nbsp;&nbsp;Job Entry of <code>Design3D</code>');

        $("div.col-md-6 > h2.legend").html('<span class="glyphicon glyphicon-qrcode"></span>&nbsp;' + $("div.col-md-6 > h2.legend").html() + '<span class="pull-right" style="font-weight:normal; font-size: 12px;">(Click values in first column to edit)</span>');
        $("ul.breadcrumb > li:first").next().remove();
        $("ul.breadcrumb > li:first").next().prepend('<span style="color: #000;" class="glyphicon glyphicon-qrcode"></span>&nbsp;&nbsp;');
    } else if ($(location).attr("href").indexOf("admin/src/design1d") != -1) {
        $("th.column-date").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-job_id").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-tag").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-status").addClass("col-lg-1 col-md-1 col-sm-1 col-xs-1");
        $("th.column-sequence").addClass("col-lg-5 col-md-5 col-sm-5 col-xs-5");

        $("td.field-tag").css("font-style", "italic");
        $("td.field-job_id").each(function() { $(this).html("<kbd>" + $(this).html() + "</kbd>"); });
        $("td.field-status").each(function() { $(this).html(render_status($(this).html())); });
        $("td.field-sequence").css("word-break", "break-all");
        $("td.field-sequence").each(function() { $(this).html('<code style="padding:0px; border-radius:0px;">' + $(this).html() + "</code>"); });

        $("th.column-date > div.text > a").html('<span class="glyphicon glyphicon-calendar"></span>&nbsp;&nbsp;Submission Date');
        $("th.column-job_id > div.text > a").html('<span class="glyphicon glyphicon-credit-card"></span>&nbsp;&nbsp;Job ID');
        $("th.column-tag > div.text > a").html('<span class="glyphicon glyphicon-tag"></span>&nbsp;&nbsp;Tag');
        $("th.column-status > div.text > a").html('<span class="glyphicon glyphicon-hourglass"></span>&nbsp;&nbsp;Status');
        $("th.column-sequence > div.text > a").html('<span class="glyphicon glyphicon-console"></span>&nbsp;&nbsp;Sequence');

        $("div.col-md-6 > h2.legend").html('<span class="glyphicon glyphicon-tint"></span>&nbsp;' + $("div.col-md-6 > h2.legend").html() + '<span class="pull-right" style="font-weight:normal; font-size: 12px;">(Click values in first column to edit)</span>');
        $("ul.breadcrumb > li:first").next().remove();
        $("ul.breadcrumb > li:first").next().prepend('<span style="color: #000;" class="glyphicon glyphicon-tint"></span>&nbsp;&nbsp;');
    } else if ($(location).attr("href").indexOf("admin/src/design2d") != -1) {
        $("th.column-date").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-job_id").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-tag").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-status").addClass("col-lg-1 col-md-1 col-sm-1 col-xs-1");
        $("th.column-sequence").addClass("col-lg-5 col-md-5 col-sm-5 col-xs-5");

        $("td.field-tag").css("font-style", "italic");
        $("td.field-job_id").each(function() { $(this).html("<kbd>" + $(this).html() + "</kbd>"); });
        $("td.field-status").each(function() { $(this).html(render_status($(this).html())); });
        $("td.field-sequence").css("word-break", "break-all");
        $("td.field-sequence").each(function() { $(this).html('<code style="padding:0px; border-radius:0px;">' + $(this).html() + "</code>"); });

        $("th.column-date > div.text > a").html('<span class="glyphicon glyphicon-calendar"></span>&nbsp;&nbsp;Submission Date');
        $("th.column-job_id > div.text > a").html('<span class="glyphicon glyphicon-credit-card"></span>&nbsp;&nbsp;Job ID');
        $("th.column-tag > div.text > a").html('<span class="glyphicon glyphicon-tag"></span>&nbsp;&nbsp;Tag');
        $("th.column-status > div.text > a").html('<span class="glyphicon glyphicon-hourglass"></span>&nbsp;&nbsp;Status');
        $("th.column-sequence > div.text > a").html('<span class="glyphicon glyphicon-console"></span>&nbsp;&nbsp;Sequence');

        $("div.col-md-6 > h2.legend").html('<span class="glyphicon glyphicon-tint"></span>&nbsp;' + $("div.col-md-6 > h2.legend").html() + '<span class="pull-right" style="font-weight:normal; font-size: 12px;">(Click values in first column to edit)</span>');
        $("ul.breadcrumb > li:first").next().remove();
        $("ul.breadcrumb > li:first").next().prepend('<span style="color: #000;" class="glyphicon glyphicon-tint"></span>&nbsp;&nbsp;');
    } else if ($(location).attr("href").indexOf("admin/src/design3d") != -1) {
        $("div.col-md-6 > h2.legend").html('<span class="glyphicon glyphicon-leaf"></span>&nbsp;' + $("div.col-md-6 > h2.legend").html() + '<span class="pull-right" style="font-weight:normal; font-size: 12px;">(Click values in first column to edit)</span>');
        $("ul.breadcrumb > li:first").next().remove();
        $("ul.breadcrumb > li:first").next().prepend('<span style="color: #000;" class="glyphicon glyphicon-leaf"></span>&nbsp;&nbsp;');
    } else if ($(location).attr("href").indexOf("admin/src/sourcedownloader") != -1) {
        $("th.column-date").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-full_name").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-affiliation").addClass("col-lg-5 col-md-5 col-sm-5 col-xs-5");
        $("th.column-email").addClass("col-lg-3 col-md-3 col-sm-3 col-xs-3");

        $("td.field-full_name").css("font-weight", "bold");
        $("td.field-email").css("text-decoration", "underline");

        $("th.column-date > div.text > a").html('<span class="glyphicon glyphicon-calendar"></span>&nbsp;&nbsp;Request Date');
        $("th.column-full_name > div.text > a").html('<span class="glyphicon glyphicon-credit-card"></span>&nbsp;&nbsp;Full Name');
        $("th.column-affiliation > div.text > a").html('<span class="glyphicon glyphicon-education"></span>&nbsp;&nbsp;Affiliation');
        $("th.column-email > div.text > a").html('<span class="glyphicon glyphicon-envelope"></span>&nbsp;&nbsp;Email');

        $("div.col-md-6 > h2.legend").html('<span class="glyphicon glyphicon-cloud-download"></span>&nbsp;' + $("div.col-md-6 > h2.legend").html() + '<span class="pull-right" style="font-weight:normal; font-size: 12px;">(Click values in first column to edit)</span>');
        $("ul.breadcrumb > li:first").next().remove();
        $("ul.breadcrumb > li:first").next().prepend('<span style="color: #000;" class="glyphicon glyphicon-cloud-download"></span>&nbsp;&nbsp;');
    } else if ($(location).attr("href").indexOf("admin/src/historyitem") != -1) {
        $("th.column-date").addClass("col-lg-3 col-md-3 col-sm-3 col-xs-3");
        $("th.column-content_html").addClass("col-lg-9 col-md-9 col-sm-9 col-xs-9");

        $("td.field-content_html").each(function() { $(this).html($(this).text()); });

        $("th.column-date > div.text > a").html('<span class="glyphicon glyphicon-calendar"></span>&nbsp;&nbsp;Display Date');
        $("th.column-content_html > div.text > a").html('<span class="glyphicon glyphicon-globe"></span>&nbsp;&nbsp;HTML Content');

        $("div.col-md-6 > h2.legend").html('<span class="glyphicon glyphicon-list-alt"></span>&nbsp;' + $("div.col-md-6 > h2.legend").html() + '<span class="pull-right" style="font-weight:normal; font-size: 12px;">(Click values in first column to edit)</span>');
        $("ul.breadcrumb > li:first").next().remove();
        $("ul.breadcrumb > li:first").next().prepend('<span style="color: #000;" class="glyphicon glyphicon-list-alt"></span>&nbsp;&nbsp;');
    } else if ($(location).attr("href").indexOf("admin/auth/user") != -1) {
        $("th.column-username").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-email").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-last_login").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-is_active").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-is_staff").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");
        $("th.column-is_superuser").addClass("col-lg-2 col-md-2 col-sm-2 col-xs-2");

        $("th.field-username").css("font-style", "italic");
        $("td.field-email").css("text-decoration", "underline");

        $("th.column-username > div.text > a").html('<span class="glyphicon glyphicon-user"></span>&nbsp;&nbsp;Username');
        $("th.column-email > div.text > a").html('<span class="glyphicon glyphicon-envelope"></span>&nbsp;&nbsp;Email Address');
        $("th.column-last_login > div.text > a").html('<span class="glyphicon glyphicon-time"></span>&nbsp;&nbsp;Last Login');
        $("th.column-is_active > div.text > a").html('<span class="glyphicon glyphicon-pawn"></span>&nbsp;&nbsp;Active');
        $("th.column-is_staff > div.text > a").html('<span class="glyphicon glyphicon-queen"></span>&nbsp;&nbsp;Staff');
        $("th.column-is_superuser > div.text > a").html('<span class="glyphicon glyphicon-king"></span>&nbsp;&nbsp;Admin');

        $("div.col-md-6 > h2.legend").html('<span class="glyphicon glyphicon-lock"></span>&nbsp;' + $("div.col-md-6 > h2.legend").html() + '<span class="pull-right" style="font-weight:normal; font-size: 12px;">(Click values in first column to edit)</span>');
        $("ul.breadcrumb > li:first").next().remove();
        $("ul.breadcrumb > li:first").next().prepend('<span style="color: #000;" class="glyphicon glyphicon-lock"></span>&nbsp;&nbsp;');

    }

});


$(window).load(function () {
    setTimeout(function() {
        $(".vDateField").each(function () {
            $(this).next().detach().appendTo($(this).parent());
            $(this).removeAttr("size");
            $(this).next().detach().insertAfter($(this).parent());
            $(this).parent().addClass("input-group").removeClass("");

            $('<div class="input-group-btn"><a class="btn btn-default" id="' + $(this).attr("id") + '_cal"><span class="glyphicon glyphicon-calendar"></span>&nbsp;&nbsp;Calendar&nbsp;&nbsp;</a><a class="btn btn-primary" id="' + $(this).attr("id") + '_today"><span class="glyphicon glyphicon-map-marker"></span>&nbsp;&nbsp;Today&nbsp;&nbsp;</a></div>').insertAfter($(this));
            $(this).css("width", "auto");

            var elem;
            if ($(this).parent().next().hasClass("datetimeshortcuts")) {
                elem = $(this).parent().next();
            } else {
                // $('<br><br>').insertBefore($(this).parent().next());
                $(this).parent().next().css("display", "block");
                elem = $(this).siblings().last();
            }
            $('#' + $(this).attr("id") + '_cal').attr("href", elem.children().last().attr("href"));
            $('#' + $(this).attr("id") + '_cal').on("click", function() {
                var self = $(this);
                setTimeout(function () {
                    $(".calendarbox.module").css("left", self.offset().left);
                    $(".calendarbox.module").css("top", self.offset().top + 50);
                }, 50);
            });
            $('#' + $(this).attr("id") + '_today').attr("href", elem.children().first().attr("href"));

            elem.css("display", "none");
            $('<p class="datetime input-group"></p>').insertBefore($(this));
            var p = $(this).prev();
            $(this).next().detach().appendTo(p);
            $(this).detach().prependTo(p);
            $("span.timezonewarning").addClass("label label-default");
        });

        $(".vTimeField").each(function () {
            $(this).next().detach().appendTo($(this).parent());
            $(this).removeAttr("size");
            $(this).next().detach().insertAfter($(this).parent());
            $(this).parent().addClass("input-group").removeClass("");

            $('<div class="input-group-btn"><a class="btn btn-default" id="' + $(this).attr("id") + '_clk"><span class="glyphicon glyphicon-time"></span>&nbsp;&nbsp;Clock&nbsp;&nbsp;</a><a class="btn btn-primary" id="' + $(this).attr("id") + '_now"><span class="glyphicon glyphicon-map-marker"></span>&nbsp;&nbsp;Now&nbsp;&nbsp;</a></div>').insertAfter($(this));
            $(this).css("width", "auto");

            var elem;
            if ($(this).parent().next().hasClass("datetimeshortcuts")) {
                elem = $(this).siblings().last();
            } else {
                // $('<br><br>').insertBefore($(this).parent().next());
                $(this).parent().next().css("display", "block");
                elem = $(this).siblings().last();
            }
            $('#' + $(this).attr("id") + '_clk').attr("href", elem.children().last().attr("href"));
            $('#' + $(this).attr("id") + '_clk').on("click", function() {
                var self = $(this);
                setTimeout(function () {
                    $(".clockbox.module").css("left", self.offset().left);
                    $(".clockbox.module").css("top", self.offset().top + 50);
                }, 50);
            });
            $('#' + $(this).attr("id") + '_now').attr("href", elem.children().first().attr("href"));

            elem.css("display", "none");
            $('<p class="datetime input-group"></p>').insertBefore($(this));
            var p = $(this).prev();
            $(this).next().detach().appendTo(p);
            $(this).detach().prependTo(p);
            $("span.timezonewarning").addClass("label label-default");
        });

        if ($(location).attr("href").indexOf("admin/auth/user") != -1) {
            // $(".vDateField").each(function () {
            //  $(this).parent().contents().filter(function () {return this.data === "Date: ";}).replaceWith("");
            // });
            // $(".vTimeField").each(function () {
            //  $(this).parent().contents().filter(function () {return this.data === "Time: ";}).replaceWith("");
            // });
            $("span.help-icon").removeClass("help help-tooltip help-icon").addClass("glyphicon glyphicon-question-sign");

            $("select").addClass("form-control").removeClass("filtered");
            $("input[placeholder='Filter']").addClass("form-control").parent().addClass("input-group");
            $("<br/>").insertAfter($("input[placeholder='Filter']").parent());
            $('<div class="input-group-addon"><span class="glyphicon glyphicon-search"></span></div>').insertAfter($("input[placeholder='Filter']"));
            $("img[src='/static/admin/img/selector-search.svg']").parent().remove();
            $('<span class="glyphicon glyphicon-question-sign"></span>').insertAfter($("img[src='/static/admin/img/icon-unknown.svg']"));
            $("img[src='/static/admin/img/icon-unknown.svg']").remove();

            $("a.selector-add").addClass("btn btn-inverse").html('<span class="glyphicon glyphicon-circle-arrow-right"></span>');
            $("a.selector-remove").addClass("btn btn-default").html('<span class="glyphicon glyphicon-circle-arrow-left"></span>');
            $("a.add-related").addClass("btn btn-blue").html('<span class="glyphicon glyphicon-plus-sign"></span>&nbsp;&nbsp;Add Group');
            $("<br/>").insertBefore($("a.selector-chooseall"));
            $("a.selector-chooseall").addClass("btn btn-info").html('<span class="glyphicon glyphicon-ok-sign"></span>&nbsp;&nbsp;Choose All');
            $("<br/>").insertBefore($("a.selector-clearall"));
            $("a.selector-clearall").addClass("btn btn-default").html('<span class="glyphicon glyphicon-remove-sign"></span>&nbsp;&nbsp;Remove All');
        }

        $("img[src$='/static/admin/img/icon-yes.svg']").each(function() {
            var newElem = $('<span class="label label-green"><span class="glyphicon glyphicon-ok-sign"></span></span>');
            $(this).replaceWith(newElem);
        });
        $("img[src$='/static/admin/img/icon-no.svg']").each(function() {
            var newElem = $('<span class="label label-danger"><span class="glyphicon glyphicon-remove-sign"></span></span>');
            $(this).replaceWith(newElem);
        });
        $("img[src$='/static/admin/img/icon-changelink.svg']").each(function() {
            var newElem = $('<span class="label label-warning"><span class="glyphicon glyphicon-edit"></span></span>');
            $(this).replaceWith(newElem);
        });
        $("img[src$='/static/admin/img/icon-addlink.svg']").each(function() {
            var newElem = $('<span class="label label-success"><span class="glyphicon glyphicon-plus-sign"></span></span>');
            $(this).replaceWith(newElem);
        });


    }, 50);

});
