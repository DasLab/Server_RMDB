var $ = django.jQuery;
var weekdayNames = new Array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');

$(document).ready(function() {
  $("ul.breadcrumb > li.active").text("System Dashboard");

  // $("#content").addClass("row").removeClass("row-fluid").removeClass("colM");
  $("#content > h2.content-title").remove();
  $("span.divider").remove();
  $("lspan").remove();

  $.ajax({
        url : "/get_ver",
        dataType: "text",
        success : function (data) {
        	var txt = data.split(/\t/);

        	$("#id_linux").html(txt[0]);
        	$("#id_python").html(txt[1]);
        	$("#id_django").html(txt[2]);
            $("#id_django_crontab").html(txt[3]);
            $("#id_django_environ").html(txt[4]);
            $("#id_mysql").html(txt[5]);
            $("#id_apache").html(txt[6]);
            $("#id_wsgi").html(txt[7]);
            $("#id_webauth").html(txt[8]);
            $("#id_ssl").html(txt[9]);
            $("#id_wallet").html(txt[10]);

            $("#id_jquery").html(txt[11]);
            $("#id_bootstrap").html(txt[12]);
            $("#id_django_suit").html(txt[13]);
            $("#id_django_adminplus").html(txt[14]);
            $("#id_django_filemanager").html(txt[15]);
            $("#id_swfobj").html(txt[16]);
            $("#id_fullcal").html(txt[17]);
            $("#id_moment").html(txt[18]);
            // $("#id_dropz").html(txt[19]);
            $("#id_ical").html(txt[20]);
            $("#id_gvizapi").html(txt[21]);

        	$("#id_ssh").html(txt[22]);
        	$("#id_git").html(txt[23]);
            $("#id_nano").html(txt[24]);
            $("#id_gdrive").html(txt[25]);
            $("#id_pandoc").html(txt[26]);
            $("#id_boto").html(txt[28]);
            $("#id_pygit").html(txt[29]);
            $("#id_slacker").html(txt[30]);
            $("#id_dropbox").html(txt[31]);

            $("#id_request").html(txt[32]);
            $("#id_simplejson").html(txt[33]);
            $("#id_curl").html(txt[27]);
            $("#id_virtualenv").html(txt[34]);
        	$("#id_pip").html(txt[35]);

            var drive_free = parseFloat(txt[44]), drive_used = parseFloat(txt[43]), drive_total = parseFloat(txt[45]);
            $("#id_drive_space > div > div.progress-bar-success").css("width", (drive_free / drive_total * 100).toString() + '%' ).html(drive_free + ' G');
            $("#id_drive_space > div > div.progress-bar-danger").css("width", (drive_used / drive_total * 100).toString() + '%' ).html(drive_used + ' G');
        	var disk_sp = txt[36].split(/\//);
            $("#id_disk_space > div > div.progress-bar-success").css("width", (parseFloat(disk_sp[0]) / (parseFloat(disk_sp[0]) + parseFloat(disk_sp[1])) * 100).toString() + '%' ).html(disk_sp[0]);
            $("#id_disk_space > div > div.progress-bar-danger").css("width", (parseFloat(disk_sp[1]) / (parseFloat(disk_sp[0]) + parseFloat(disk_sp[1])) * 100).toString() + '%' ).html(disk_sp[1]);
        	var mem_sp = txt[37].split(/\//);
            $("#id_memory > div > div.progress-bar-success").css("width", (parseFloat(mem_sp[0]) / (parseFloat(mem_sp[0]) + parseFloat(mem_sp[1])) * 100).toString() + '%' ).html(mem_sp[0]);
            $("#id_memory > div > div.progress-bar-danger").css("width", (parseFloat(mem_sp[1]) / (parseFloat(mem_sp[0]) + parseFloat(mem_sp[1])) * 100).toString() + '%' ).html(mem_sp[1]);

        	$("#id_backup").html('<span style="color:#00f;">' + txt[38] + '</span>');
        	var cpu = txt[39].split(/\//);
        	$("#id_cpu").html('<span style="color:#f00;">' + cpu[0] + '</span> | <span style="color:#080;">' + cpu[1] + '</span> | <span style="color:#00f;">' + cpu[2] + '</span>');

            $("#id_base_dir").html('<code>' + txt[40] + '</code>');
            $("#id_media_root").html('<code>' + txt[41] + '</code>');
            $("#id_static_root").html('<code>' + txt[42] + '</code>');
    	}
    });

    $.ajax({
        url : "/admin/backup_form",
        dataType: "json",
        success : function (data) {
            $("#id_week_backup").html($("#id_week_backup").html() + '<br/>On <span class="label label-primary">' + data.time_backup + '</span> every <span class="label label-inverse">' + weekdayNames[data.day_backup] + '</span> (UTC)');
            $("#id_week_upload").html($("#id_week_upload").html() + '<br/>On <span class="label label-primary">' + data.time_upload + '</span> every <span class="label label-inverse">' + weekdayNames[data.day_upload] + '</span> (UTC)');

            if (data.time_backup) {
                $("#id_week_backup_stat").html('<p class="lead"><span class="label label-green"><span class="glyphicon glyphicon-ok-sign"></span></span></p>');
            } else {
                $("#id_week_backup_stat").html('<p class="lead"><span class="label label-danger"><span class="glyphicon glyphicon-remove-sign"></span></span></p>');
            }
            if (data.time_upload) {
                $("#id_week_upload_stat").html('<p class="lead"><span class="label label-green"><span class="glyphicon glyphicon-ok-sign"></span></span></p>');
            } else {
                $("#id_week_upload_stat").html('<p class="lead"><span class="label label-danger"><span class="glyphicon glyphicon-remove-sign"></span></span></p>');
            }
        }
    });

   $.ajax({
        url : "/admin/ssl_dash",
        dataType: "json",
        success : function (data) {
            $("#id_ssl_exp").html('<span class="label label-inverse">' + data.exp_date + '</span> (UTC)');
        }
    });

   $.ajax({
        url : "/admin/dash_dash",
        dataType: "json",
        success : function (data) {
            $("#id_dash_aws").html(data.t_aws);
            $("#id_dash_ga").html(data.t_ga);
            $("#id_dash_git").html(data.t_git);
            $("#id_dash_slack").html(data.t_slack);
            $("#id_dash_dropbox").html(data.t_dropbox);
            $("#id_dash_cal").html(data.t_cal);
            $("#id_dash_sch").html(data.t_sch);
        }
    });



});

