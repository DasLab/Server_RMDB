var $ = django.jQuery;
var weekdayNames = new Array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');

$(document).ready(function() {
    $("ul.breadcrumb > li.active").text("System Dashboard");

    // $("#content").addClass("row").removeClass("row-fluid").removeClass("colM");
    $("#content > h2.content-title").remove();
    $("span.divider").remove();
    $("lspan").remove();

    $.ajax({
        url : "/admin/get_backup",
        dataType: "text",
        success : function (data) {
            var txt = data.split(/\t/);

            $("#id_news_n").html('<i>' + txt[0] + '</i>');
            $("#id_news_s").html('<span style="color:#00f;">' + txt[1] + '</span>');
            $("#id_member_n").html('<i>' + txt[2] + '</i>');
            $("#id_member_s").html('<span style="color:#00f;">' + txt[3] + '</span>');
            $("#id_pub_n").html('<i>' + txt[4] + '</i>');
            $("#id_pub_s").html('<span style="color:#00f;">' + txt[5] + '</span>');
            $("#id_rot_n").html('<i>' + txt[6] + '</i>');
            $("#id_rot_s").html('<span style="color:#00f;">' + txt[7] + '</span>');
            $("#id_spe_n").html('<i>' + txt[8] + '</i>');
            $("#id_spe_s").html('<span style="color:#00f;">' + txt[9] + '</span>');

            $("#id_mysql_s").html('<span style="color:#00f;">' + txt[10] + '</span>');
            $("#id_static_s").html('<span style="color:#00f;">' + txt[11] + '</span>');
            $("#id_apache_s").html('<span style="color:#00f;">' + txt[12] + '</span>');
            $("#id_mysql_p").html($("#id_mysql_p").html() + '<br/><code>' + txt[13] + '</code>');
            $("#id_static_p").html($("#id_static_p").html() + '<br/><code>' + txt[14] + '</code>');
            $("#id_apache_p").html($("#id_apache_p").html() + '<br/><code>' + txt[15] + '</code>');

            var gdrive = txt[16].split(/~|~/);
            var names = [], sizes = [], times = [];
            for (var i = 0; i < gdrive.length; i += 12) {
                names.push(gdrive[i+2]);
                sizes.push(gdrive[i+4] + ' ' + gdrive[i+6]);
                times.push(gdrive[i+8] + ' ' + gdrive[i+10]);
            }
            var html = '';
            for (var i = 0; i < names.length; i++) {
                html += '<tr><td><code>' + names[i] + '</code></td><td><span class="label label-primary">' + times[i] + '</span></td><td><span style="color:#00f;">' + sizes[i] + '</span></td></tr>'
            }
            html += '<tr><td colspan="3" style="padding: 0px;"></td></tr>'
            $("#gdrive_list").html(html);

        }
    });

  $.ajax({
        url : "/admin/get_ver",
        dataType: "text",
        success : function (data) {
            var txt = data.split(/\t/);
            var drive_free = parseFloat(txt[44]), drive_used = parseFloat(txt[43]), drive_total = parseFloat(txt[45]);
            $("#id_drive_space > div > div.progress-bar-success").css("width", (drive_free / drive_total * 100).toString() + '%' ).html(drive_free + ' G');
            $("#id_drive_space > div > div.progress-bar-danger").css("width", (drive_used / drive_total * 100).toString() + '%' ).html(drive_used + ' G');
            var disk_sp = txt[36].split(/\//);
            $("#id_disk_space > div > div.progress-bar-success").css("width", (parseFloat(disk_sp[0]) / (parseFloat(disk_sp[0]) + parseFloat(disk_sp[1])) * 100).toString() + '%' ).html(disk_sp[0]);
            $("#id_disk_space > div > div.progress-bar-danger").css("width", (parseFloat(disk_sp[1]) / (parseFloat(disk_sp[0]) + parseFloat(disk_sp[1])) * 100).toString() + '%' ).html(disk_sp[1]);
        }
    });

    $.ajax({
        url : "/admin/backup_form",
        dataType: "json",
        success : function (data) {
            $("#id_time_backup").val(data.time_backup);
            $("#id_day_backup").val(data.day_backup);
            $("#id_time_upload").val(data.time_upload);
            $("#id_day_upload").val(data.day_upload);
            if (!data.time_backup || !data.day_backup) {
                $("#banner_backup").removeClass("alert-success").addClass("alert-danger");
                $("#sign_backup").removeClass("glyphicon-ok-sign").addClass("glyphicon-remove-sign");
            }
            if (!data.time_upload || !data.day_upload) {
                $("#banner_sync").removeClass("alert-success").addClass("alert-danger");
                $("#sign_sync").removeClass("glyphicon-ok-sign").addClass("glyphicon-remove-sign");
            }

            $("#id_time_backup").trigger("change");
            $("#id_time_upload").trigger("change");
            $("#modal_backup").html('On <span class="label label-primary">' + $("#id_time_backup").val() + '</span> every <span class="label label-inverse">' + weekdayNames[$("#id_day_backup").val()] + '</span> (UTC).');
            $("#modal_upload").html('On <span class="label label-primary">' + $("#id_time_upload").val() + '</span> every <span class="label label-inverse">' + weekdayNames[$("#id_day_upload").val()] + '</span> (UTC).');
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

});

