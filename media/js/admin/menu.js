var $ = django.jQuery;
var side_toggle = true;

function navbar_collapse() {
    if ($("#nav_collapse").is(":visible")) {
        side_toggle = true;
        $("#nav_toggle").trigger("click");
        $("#nav_toggle").hide();
        $("#nav_external").unbind();
        $("#nav_group").unbind();
        $("#nav_time").unbind();
        $("#nav_email").unbind();
        $("#nav_upload").unbind();
        $("#nav_profile").unbind();

        $("#nav_logo").css("width", "auto");
    } else {
        $("#nav_toggle").show();
        // $("#nav_time").hover(
        //   function(){ $("#nav_meetings").fadeIn(); },
        //   function(){ $("#nav_meetings").fadeOut(); }
        // );
        $("#nav_external").hover(
          function(){ $("#nav_external_text").fadeIn(250).siblings().css("color", "#ff912e"); },
          function(){ $("#nav_external_text").fadeOut(250).siblings().css("color", "#fff"); }
        );
        $("#nav_group").hover(
          function(){ $("#nav_group_text").fadeIn(250).siblings().css("color", "#eeb211"); },
          function(){ $("#nav_group_text").fadeOut(250).siblings().css("color", "#fff"); }
        );

        $(".dropdown-toggle").dropdown();
        $(".dropdown").hover(
          function(){ $(this).addClass("open"); },
          function(){ $(this).removeClass("open"); }
        );
        $("#nav_logo").css("width", parseInt($("#nav_logo").css("width")) + 250 - parseInt($("#nav_external").position().left));
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
    } else if ($(location).attr("href").indexOf("admin/src/news") != -1) {
    	$("#nav_news").addClass("active");
    	$("#nav_global").addClass("active");
    	$("#nav_global_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #50cc32");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-globe"></span>&nbsp;&nbsp;<a href="">Global Site</a></li>').insertAfter($("ul.breadcrumb > li:first"));
	} else if ($(location).attr("href").indexOf("admin/src/member") != -1) {
    	$("#nav_member").addClass("active");
    	$("#nav_global").addClass("active");
    	$("#nav_global_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #50cc32");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-globe"></span>&nbsp;&nbsp;<a href="">Global Site</a></li>').insertAfter($("ul.breadcrumb > li:first"));
    } else if ($(location).attr("href").indexOf("admin/src/publication") != -1) {
    	$("#nav_pub").addClass("active");
    	$("#nav_global").addClass("active");
    	$("#nav_global_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #50cc32");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-globe"></span>&nbsp;&nbsp;<a href="">Global Site</a></li>').insertAfter($("ul.breadcrumb > li:first"));
	} else if ($(location).attr("href").indexOf("admin/export") != -1) {
    	$("#nav_export").addClass("active");
    	$("#nav_global").addClass("active");
    	$("#nav_global_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #008080");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-globe"></span>&nbsp;&nbsp;<a href="">Global Site</a></li>').insertAfter($("ul.breadcrumb > li:first"));
	} else if ($(location).attr("href").indexOf("admin/auth/user") != -1) {
    	$("#nav_auth").addClass("active");
    	$("#nav_internal").addClass("active");
    	$("#nav_internal_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #ff912e");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Internal Site</a></li>').insertAfter($("ul.breadcrumb > li:first"));
	} else if ($(location).attr("href").indexOf("admin/src/flashslide") != -1) {
    	$("#nav_flash").addClass("active");
    	$("#nav_internal").addClass("active");
    	$("#nav_internal_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #eeb211");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Internal Site</a></li>').insertAfter($("ul.breadcrumb > li:first"));
 	} else if ($(location).attr("href").indexOf("admin/src/eternayoutube") != -1) {
    	$("#nav_eterna").addClass("active");
    	$("#nav_internal").addClass("active");
    	$("#nav_internal_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #eeb211");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Internal Site</a></li>').insertAfter($("ul.breadcrumb > li:first"));
	} else if ($(location).attr("href").indexOf("admin/src/rotationstudent") != -1) {
    	$("#nav_rot").addClass("active");
    	$("#nav_internal").addClass("active");
    	$("#nav_internal_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #eeb211");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Internal Site</a></li>').insertAfter($("ul.breadcrumb > li:first"));
 	} else if ($(location).attr("href").indexOf("admin/src/presentation") != -1) {
    	$("#nav_archive").addClass("active");
    	$("#nav_internal").addClass("active");
    	$("#nav_internal_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #eeb211");
        $('<li><span style="color: #000;" class="glyphicon glyphicon-inbox"></span>&nbsp;&nbsp;<a href="">Internal Site</a></li>').insertAfter($("ul.breadcrumb > li:first"));
 	} else if ($(location).attr("href").indexOf("admin/doc") != -1) {
    	$("#nav_doc").addClass("active");
    	$("#nav_doc_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #c28fdd")
 	} else {
    	$("#nav_home").addClass("active");
    	$("#nav_home_lg").addClass("active");
    	$("ul.breadcrumb").css("border-bottom", "5px solid #3ed4e7")
	}

	$("#nav_toggle").on("click", function() {
		if (side_toggle) {
			$(".nav-ul").hide();
			$(".nav-ul-lg").show();
			$("#wrapper").css("padding-left", "50px");
			$("#sidebar-wrapper").css({"margin-left":"-65px", "left":"65px", "width":"65px"});
		} else {
			$(".nav-ul-lg").hide();
			$(".nav-ul").not(".nav-ul-lg").show();
			$("#wrapper").css("padding-left", "235px");
			$("#sidebar-wrapper").css({"margin-left":"-250px", "left":"250px", "width":"250px"});
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
        $("#wrapper").css("width", $(window).width() - $("sidebar-wrapper").width() - 20);
    }, 200));
});


