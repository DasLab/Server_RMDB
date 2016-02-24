var $ = django.jQuery;
var side_toggle = true;

function navbar_collapse() {
    if ($("#nav_collapse").is(":visible")) {
        side_toggle = true;
        $("#nav_toggle").trigger("click");
        $("#nav_toggle").hide();
        $("#nav_public").unbind();
        $("#nav_time").unbind();
        $("#nav_profile").unbind();

        $("#nav_logo").css("width", "auto");
    } else {
        $("#nav_toggle").show();
        $("#nav_public").hover(
          function(){ $("#nav_public_text").fadeIn(250).siblings().css("color", "#eeb211"); },
          function(){ $("#nav_public_text").fadeOut(250).siblings().css("color", "#fff"); }
        );

        $(".dropdown-toggle").dropdown();
        $(".dropdown").hover(
          function(){ $(this).addClass("open"); },
          function(){ $(this).removeClass("open"); }
        );
        $("#nav_logo").css("width", parseInt($("#nav_logo").css("width")) + 250 - parseInt($("#nav_public").position().left));
    }
}


$(document).ready(function () {
    $('i[class^="icon"]').each(function() {
        $(this).replaceWith('<span class="glyphicon glyph' + $(this).attr("class") + '"></span>&nbsp;&nbsp;');
    });
    $(".nav-ul-lg").css("display", "none");

    // $(".form-search > span.glyphicon").remove();
    // $(".form-search > input.submit").attr("id", "search_submit");
    // $("#search_submit").replaceWith("<button type='submit' class='submit form-control' id='search_submit' style='border:none;'><span class='glyphicon glyphicon-search'></span>&nbsp;</button>");

    if ($(location).attr("href").indexOf("admin/apache") != -1) {
        $("#nav_apache").addClass("active");
        $("#nav_sys").addClass("active");
        $("#nav_sys_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #ff5c2b");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-cog"></span>&nbsp;&nbsp;<a href="">System</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/aws") != -1) {
        $("#nav_aws").addClass("active");
        $("#nav_sys").addClass("active");
        $("#nav_sys_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #ff5c2b");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-cog"></span>&nbsp;&nbsp;<a href="">System</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/ga") != -1) {
        $("#nav_ga").addClass("active");
        $("#nav_sys").addClass("active");
        $("#nav_sys_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #ff5c2b");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-cog"></span>&nbsp;&nbsp;<a href="">System</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/git") != -1) {
        $("#nav_git").addClass("active");
        $("#nav_sys").addClass("active");
        $("#nav_sys_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #ff5c2b");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-cog"></span>&nbsp;&nbsp;<a href="">System</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/dir") != -1) {
        $("#nav_dir").addClass("active");
        $("#nav_sys").addClass("active");
        $("#nav_sys_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #ff69bc");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-cog"></span>&nbsp;&nbsp;<a href="">System</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/backup") != -1) {
        $("#nav_backup").addClass("active");
        $("#nav_sys").addClass("active");
        $("#nav_sys_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #ff69bc");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-cog"></span>&nbsp;&nbsp;<a href="">System</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/src/jobids") != -1) {
        $("#nav_job_id").addClass("active");
        $("#nav_job").addClass("active");
        $("#nav_job_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #50cc32");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Job Management</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/src/jobgroups") != -1) {
        $("#nav_job_group").addClass("active");
        $("#nav_job").addClass("active");
        $("#nav_job_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #50cc32");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Job Management</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/src/design1d") != -1) {
        $("#nav_design_1d").addClass("active");
        $("#nav_job").addClass("active");
        $("#nav_job_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #50cc32");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Job Management</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/src/design2d") != -1) {
        $("#nav_design_2d").addClass("active");
        $("#nav_job").addClass("active");
        $("#nav_job_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #50cc32");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Job Management</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/src/design3d") != -1) {
        $("#nav_design_3d").addClass("active");
        $("#nav_job").addClass("active");
        $("#nav_job_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #50cc32");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Job Management</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/auth/user") != -1) {
        $("#nav_auth").addClass("active");
        $("#nav_user").addClass("active");
        $("#nav_user_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #ff912e");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">User Management</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/src/sourcedownloader") != -1) {
        $("#nav_source_download").addClass("active");
        $("#nav_user").addClass("active");
        $("#nav_user_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #ff912e");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">User Management</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/src/historyitem") != -1) {
        $("#nav_history_item").addClass("active");
        $("#nav_user").addClass("active");
        $("#nav_user_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #ff912e");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">User Management</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/doc_django") != -1) {
        $("#nav_django").addClass("active");
        $("#nav_doc").addClass("active");
        $("#nav_doc_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #c28fdd");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-book"></span>&nbsp;&nbsp;<a href="">Documentation</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/doc_cherrypy") != -1) {
        $("#nav_cherrypy").addClass("active");
        $("#nav_doc").addClass("active");
        $("#nav_doc_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #c28fdd");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-book"></span>&nbsp;&nbsp;<a href="">Documentation</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else {
        $("#nav_home").addClass("active");
        $("#nav_home_lg").addClass("active");
        $("ul.breadcrumb").css("border-bottom", "5px solid #3ed4e7");
    }

    $("#nav_toggle").on("click", function() {
        if (side_toggle) {
            $(".nav-ul").hide();
            $(".nav-ul-lg").show();
            $("#wrapper").css("padding-left", "50px");
            $("#sidebar-wrapper").css({"margin-left":"-65px", "left":"65px", "width":"65px"});
        } else {
            $("#wrapper").css("padding-left", "235px");
            $("#sidebar-wrapper").css({"margin-left":"-250px", "left":"250px", "width":"250px"});
            setTimeout(function() {
                $(".nav-ul-lg").hide();
                $(".nav-ul").not(".nav-ul-lg").show();
            }, 400);
        }
        side_toggle = !side_toggle;
    });
    $("#wrapper").css("width", (parseInt($("#wrapper").css("width")) + 15).toString() + "px");

    $("ul.breadcrumb").css({"border-radius":"0px", "height":"50px"}).addClass("lead");
    $("ul.breadcrumb > li:first").prepend('<span style="color: #000;" class="glyphicon glyphicon-home"></span>&nbsp;&nbsp;');

    $(".dropdown-toggle").dropdown();
    $(".dropdown").hover(
      function(){ $(this).addClass("open"); },
      function(){ $(this).removeClass("open"); }
    );
    navbar_collapse();

    // $('.left-nav > ul > li > ul > li > a[href="/admin/aws/"]').attr("disabled", "disabled").css("text-decoration", "line-through").attr("href", "");
});


$(window).on("resize", function() {
    clearTimeout($.data(this, 'resizeTimer'));
    $.data(this, 'resizeTimer', setTimeout(function() {
        navbar_collapse();
        $("#wrapper").css("width", $(window).width() - $("#sidebar-wrapper").width() - 20);
    }, 200));
});


