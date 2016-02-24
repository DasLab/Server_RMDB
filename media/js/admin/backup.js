var $ = django.jQuery;
var weekdayNames = new Array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');

$(document).ready(function() {
    $("ul.breadcrumb > li.active").text("System Dashboard");

    // $("#content").addClass("row").removeClass("row-fluid").removeClass("colM");
    $("#content > h2.content-title").remove();
    $("span.divider").remove();
    $("lspan").remove();

    $.ajax({
        url : "/admin/get_backup/",
        dataType: "json",
        success : function (data) {
            $("#id_design_1d").html('<i>' + data['1d'][0] + '</i>');
            $("#id_design_1d_s").html('<span style="color:#00f;">' + data['1d'][1] + '</span>');
            $("#id_design_2d").html('<i>' + data['2d'][0] + '</i>');
            $("#id_design_2d_s").html('<span style="color:#00f;">' + data['2d'][1] + '</span>');
            $("#id_design_3d").html('<i>' + data['3d'][0] + '</i>');
            $("#id_design_3d_s").html('<span style="color:#00f;">' + data['3d'][1] + '</span>');

            $("#id_mysql_s").html('<span style="color:#00f;">' + data.backup.mysql[1] + '</span>');
            $("#id_static_s").html('<span style="color:#00f;">' + data.backup.data[1] + '</span>');
            $("#id_apache_s").html('<span style="color:#00f;">' + data.backup.apache[1] + '</span>');
            $("#id_config_s").html('<span style="color:#00f;">' + data.backup.config[1] + '</span>');
            $("#id_mysql_p").html($("#id_mysql_p").html() + '<br/><code>' + data.backup.mysql[0] + '</code>');
            $("#id_static_p").html($("#id_static_p").html() + '<br/><code>' + data.backup.data[0] + '</code>');
            $("#id_apache_p").html($("#id_apache_p").html() + '<br/><code>' + data.backup.apache[0] + '</code>');
            $("#id_config_p").html($("#id_config_p").html() + '<br/><code>' + data.backup.config[0] + '</code>');

            var html = '';
            for (var i = 0; i < data.gdrive.length; i++) {
                html += '<tr><td><code>' + data.gdrive[i][0] + '</code></td><td><span class="label label-primary">' + data.gdrive[i][2] + '</span></td><td><span style="color:#00f;">' + data.gdrive[i][1] + '</span></td></tr>';
            }
            html += '<tr><td colspan="3" style="padding: 0px;"></td></tr>';
            $("#gdrive_list").html(html);

        }
    });

    $.ajax({
        url : "/admin/get_ver/",
        dataType: "json",
        success : function (data) {
            var drive_used = parseFloat(data._drive[0]), drive_free = parseFloat(data._drive[1]), drive_total = parseFloat(data._drive[2]);
            $("#id_drive_space > div > div.progress-bar-success").css("width", (drive_free / drive_total * 100).toString() + '%' ).html(drive_free + ' G');
            $("#id_drive_space > div > div.progress-bar-danger").css("width", (100 - drive_free / drive_total * 100).toString() + '%' ).html(drive_used + ' G');
            $("#id_disk_space > div > div.progress-bar-success").css("width", (parseFloat(data._disk[0]) / (parseFloat(data._disk[0]) + parseFloat(data._disk[1])) * 100).toString() + '%' ).html(data._disk[0]);
            $("#id_disk_space > div > div.progress-bar-danger").css("width", (parseFloat(data._disk[1]) / (parseFloat(data._disk[0]) + parseFloat(data._disk[1])) * 100).toString() + '%' ).html(data._disk[1]);
        }
    });


    $("#id_time_backup, #id_day_backup").on("change", function() {
        var time = $("#id_time_backup").val();
        var backup = new Date(Date.UTC(2000, 0, parseInt($("#id_day_backup").val()) + 2, time.split(':')[0], time.split(':')[1], 0));
        $("#time_backup_pdt").html(backup.toLocaleTimeString());
        $("#day_backup_pdt").html(weekdayNames[backup.getDay()]);
    });
    $("#id_time_upload, #id_day_upload").on("change", function() {
        var time = $("#id_time_upload").val();
        var backup = new Date(Date.UTC(2000, 0, parseInt($("#id_day_upload").val()) + 2, time.split(':')[0], time.split(':')[1], 0));
        $("#time_upload_pdt").html(backup.toLocaleTimeString());
        $("#day_upload_pdt").html(weekdayNames[backup.getDay()]);
    });

    if (!$("#id_time_backup").val() || !$("#id_day_backup").val()) {
        $("#banner_backup").removeClass("alert-success").addClass("alert-danger");
        $("#sign_backup").removeClass("glyphicon-ok-sign").addClass("glyphicon-remove-sign");
    }
    if (!$("#id_time_upload").val() || !$("#id_day_upload").val()) {
        $("#banner_sync").removeClass("alert-success").addClass("alert-danger");
        $("#sign_sync").removeClass("glyphicon-ok-sign").addClass("glyphicon-remove-sign");
    }

    $("#id_time_backup").trigger("change");
    $("#id_time_upload").trigger("change");
    $("#modal_backup").html('On <span class="label label-primary">' + $("#id_time_backup").val() + '</span> every <span class="label label-inverse">' + weekdayNames[$("#id_day_backup").val()] + '</span> (UTC).');
    $("#modal_upload").html('On <span class="label label-primary">' + $("#id_time_upload").val() + '</span> every <span class="label label-inverse">' + weekdayNames[$("#id_day_upload").val()] + '</span> (UTC).');

});

