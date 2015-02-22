function init_panel_size() {
	$(".left_close").removeClass("visible").hide();
	$("#left_panel").css("width", $(window).width()/2);
	$("#left_panel").css("top", parseInt($(".navbar-fixed-top").css("height")));
	$("#left_panel").css("height", $(window).height() - parseInt($(".navbar-fixed-top").css("height")));
	$(".side_block").css("max-height", parseInt($("#left_panel").css("height")) - 20);
	$("#left-buttons").css("margin-top", parseInt($("#left_panel").css("height"))*0.8
		-parseInt($("#left-buttons").css("height"))-parseInt($(".left_close").css("height"))*2);

	$("#img_panel").css("width", $(window).width() - 75);
	$("#img_panel").css("height", "325px");
	$("#img_panel").css("top", $(window).height() - parseInt($("#img_panel").css("height")));
	$("#img-buttons").css("margin-top", 
		parseInt($("#left-buttons").css("height"))+parseInt($("#left-buttons").css("margin-top"))
		-parseInt($("#img_panel").css("top"))+parseInt($(".navbar-fixed-top").css("height"))-1);
	$("#svg_parent").css("width", parseInt($("#panel_svg").css("height"))-90);

	$("#set_panel").css("max-width", "400px");
	$("#set_panel").css("width", $(window).width()*0.33);
	$("#set_panel").css("top", parseInt($(".navbar-fixed-top").css("height")));
	$("#set_panel").css("height", $(window).height() - parseInt($(".navbar-fixed-top").css("height")));

	$("#left_panel").css({"margin-left":"-"+$("#left_panel").css("width")}).removeClass("visible");
	$("#img_panel").css({"margin-left":"-"+$("#img_panel").css("width")}).removeClass("visible");
	$("#set_panel").css({"margin-right":"-"+$("#set_panel").css("width")}).removeClass("visible");
}


$(document).ready(function() {
	$(".dropdown-toggle").removeClass("active");
	$("#nav_browse").addClass("active");
	$("#nav_logo").css("text-decoration","none");

	init_panel_size();
	$(".left_group").on("click", function() {		
		if (!$("#left_panel").hasClass("visible")) {
			$("#left_panel").addClass("visible").animate({"margin-left":"0px"});
			$(".left_close").addClass("visible").show();
			$("#left-buttons").css("margin-top", parseInt($("#left-buttons").css("margin-top"))-parseInt($(".left_close").css("height")));
			$("#left_panel").css("z-index", "100");
			$("#img_panel").css("z-index", "1");
		}	
	});
	$(".left_close").on("click", function() {
		$("#left_panel").removeClass("visible").animate({"margin-left":"-"+$("#left_panel").css("width")});
		$(".left_close").removeClass("visible").hide();
		$("#left-buttons").css("margin-top", parseInt($("#left-buttons").css("margin-top"))+parseInt($(".left_close").css("height")));
	});
	$(".left_alone").on("click", function() {		
		if (!$("#img_panel").hasClass("visible")) {
			$("#img_panel").addClass("visible").animate({"margin-left":"0px"}).css("z-index", "100");
			$("#left_panel").css("z-index", "1");
		} else {
			$("#img_panel").removeClass("visible").animate({"margin-left":"-"+$("#img_panel").css("width")});
		}	
	});
	$("#btn-set").on("click", function() {		
		if (!$("#set_panel").hasClass("visible")) {
			$("#set_panel").addClass("visible").animate({"margin-right":"0px"}).css("z-index", "100");
			$("#img_panel").css("z-index", "1");
		} else {
			$("#set_panel").removeClass("visible").animate({"margin-right":"-"+$("#set_panel").css("width")});
		}	
	});
	$("#close-set").on("click", function() {
		$("#set_panel").removeClass("visible").animate({"margin-right":"-"+$("#set_panel").css("width")});
		$(".right_close").removeClass("visible").hide();
		$("#set-buttons").css("margin-top", parseInt($("#set-buttons").css("margin-top"))+parseInt($(".right_close").css("height")));
	});

	$("#dl_rdat, #dl_isatab").on("click", function() {$(window).unbind();});

    var col_h = Math.max($("#panel_con").height(), $("#panel_cit").height()) + 15;
    $("#panel_con").css("height", col_h);
    $("#panel_cit").css("height", col_h);

    $("#show_seq").on("click", function() {
		if ($(this).is(':checked')) {
			seq_overlay(json);
		} else {
			d3.selectAll("text.overlay").transition().duration(250).style("opacity", 0).remove();
		}
	});
	$("#show_color_seq").attr("checked", true);
    $("#show_color_seq").on("click", function() {
		if ($(this).is(':checked')) {
			d3.selectAll("text.color").transition().duration(250).attr("fill", function(d) { 
				if (d.seq) {
					return get_nt_color(d.seq);
				} else {
					return get_nt_color(d.substring(0,1));
				}
			});
		} else {
			d3.selectAll("text.color").transition().duration(250).attr("fill", "black");
		}
	});
});


$(window).on("resize", function() {
	clearTimeout($.data(this, 'resizeTimer'));
	$.data(this, 'resizeTimer', setTimeout(function() {init_panel_size();}, 200));
});


$(window).on("load", function() {
	init_panel_size();
	$("#left_panel").animate({"margin-left":"0px"},0).removeClass("visible").animate({"margin-left":"-"+$("#left_panel").css("width")}, 1000);
	$(".left_close").removeClass("visible").hide();
	$("#img_panel").animate({"margin-left":"0px"},0).removeClass("visible").animate({"margin-left":"-"+$("#img_panel").css("width")}, 1000);
	$("#set_panel").animate({"margin-right":"0px"},0).removeClass("visible").animate({"margin-right":"-"+$("#set_panel").css("width")}, 1000);
});
