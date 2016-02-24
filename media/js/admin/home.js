var $ = django.jQuery;
var weekdayNames = new Array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');

$(document).ready(function() {
  $("ul.breadcrumb > li.active").text("System Dashboard");

  // $("#content").addClass("row").removeClass("row-fluid").removeClass("colM");
  $("#content > h2.content-title").remove();
  $("span.divider").remove();
  $("lspan").remove();

  $.ajax({
        url : "/admin/get_ver/",
        dataType: "json",
        success : function (data) {
            $("#id_linux").html(data.linux);
            $("#id_python").html(data.python);
            $("#id_django").html(data.django);
            $("#id_django_crontab").html(data.django_crontab);
            $("#id_django_environ").html(data.django_environ);
            $("#id_mysql").html(data.mysql);
            $("#id_apache").html(data.apache);
            $("#id_wsgi").html(data.mod_wsgi);
            $("#id_ssl").html(data.openssl);

            $("#id_jquery").html(data.jquery);
            $("#id_bootstrap").html(data.bootstrap);
            $("#id_django_suit").html(data.django_suit);
            $("#id_django_adminplus").html(data.django_adminplus);
            $("#id_django_filemanager").html(data.django_filemanager);
            $("#id_d3").html(data.d3);
            $("#id_zclip").html(data.zclip);
            $("#id_gvizapi").html(data.gviz_api);

            $("#id_ssh").html(data.ssh);
            $("#id_git").html(data.git);
            $("#id_llvm").html(data.llvm);
            $("#id_nano").html(data.nano);
            $("#id_gdrive").html(data.gdrive);
            $("#id_zip").html(data.zip);
            $("#id_curl").html(data.curl);
            $("#id_boto").html(data.boto);
            $("#id_pygit").html(data.pygithub);

            $("#id_xlwt").html(data.xlwt);
            $("#id_request").html(data.requests);
            $("#id_simplejson").html(data.simplejson);
            $("#id_virtualenv").html(data.virtualenv);
            $("#id_pip").html(data.pip);

            $("#id_numpy").html(data.numpy);
            $("#id_scipy").html(data.scipy);
            $("#id_matplotlib").html(data.matplotlib);
            $("#id_numba").html(data.numba);

            $("#id_yui").html(data.yuicompressor);
            $("#id_rdatkit").html(data.RDAT_Kit);
            $("#id_primerize").html(data.NA_Thermo);

            var drive_used = parseFloat(data._drive[0]), drive_free = parseFloat(data._drive[1]), drive_total = parseFloat(data._drive[2]);
            $("#id_drive_space > div > div.progress-bar-success").css("width", (drive_free / drive_total * 100).toString() + '%' ).html(drive_free + ' G');
            $("#id_drive_space > div > div.progress-bar-danger").css("width", (100 - drive_free / drive_total * 100).toString() + '%' ).html(drive_used + ' G');
            $("#id_disk_space > div > div.progress-bar-success").css("width", (parseFloat(data._disk[0]) / (parseFloat(data._disk[0]) + parseFloat(data._disk[1])) * 100).toString() + '%' ).html(data._disk[0]);
            $("#id_disk_space > div > div.progress-bar-danger").css("width", (parseFloat(data._disk[1]) / (parseFloat(data._disk[0]) + parseFloat(data._disk[1])) * 100).toString() + '%' ).html(data._disk[1]);
            $("#id_memory > div > div.progress-bar-success").css("width", (parseFloat(data._mem[0]) / (parseFloat(data._mem[0]) + parseFloat(data._mem[1])) * 100).toString() + '%' ).html(data._mem[0]);
            $("#id_memory > div > div.progress-bar-danger").css("width", (parseFloat(data._mem[1]) / (parseFloat(data._mem[0]) + parseFloat(data._mem[1])) * 100).toString() + '%' ).html(data._mem[1]);
            $("#id_cpu").html('<span style="color:#f00;">' + data._cpu[0] + '</span> | <span style="color:#080;">' + data._cpu[1] + '</span> | <span style="color:#00f;">' + data._cpu[2] + '</span>');

            $("#id_base_dir").html('<code>' + data._path.root + '</code>');
            $("#id_media_root").html('<code>' + data._path.media + '</code>');
            $("#id_static_root").html('<code>' + data._path.data + '</code>');
            $("#id_primerize_path").html('<code>' + data._path.NA_Thermo + '</code>');
            $("#id_rdatkit_path").html('<code>' + data._path.RDAT_Kit + '</code>');
        }
    });
    $.ajax({
        url : "/admin/get_backup/",
        dataType: "json",
        success : function (data) {
            $("#id_backup").html('<span style="color:#00f;">' + data.backup.all + '</span>');
        }
    });

    $.ajax({
        url : "/admin/backup_form/",
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
        url : "/admin/ssl_dash/",
        dataType: "json",
        success : function (data) {
            $("#id_ssl_exp").html('<span class="label label-inverse">' + data.exp_date + '</span> (UTC)');
        }
    });

});

