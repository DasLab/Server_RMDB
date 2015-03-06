function fill_category_list(data, tag) {
	var pan_html = '';
	for (c in data) {
		if (tag == "Eterna") {
			pan_html = '<table class="table table-hover table-striped"><tr><th class="col-md-2"></th><th class="col-md-2"></th><th class="col-md-8"></th></tr>';
			for (e in data[c].SS_entry) {
				pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/repository/detail/' + data[c].SS_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].SS_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Standard State</span></p><i>Version:</i> <mark>' + data[c].SS_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].SS_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].SS_entry[e].data_count + '</code></p></td><td id="' + data[c].SS_entry[e].rmdb_id + '" class="eterna-subpanel"><div style="height:220px;overflow:hidden;"><a href="/repository/detail/' + data[c].SS_entry[e].rmdb_id + '" class="row browse-rotate thumbnail pull-left" style="left:-300px;"><img src="/site_data/thumbs/' + data[c].SS_entry[e].cid + '/' + convertToSlug(data[c].name) + '.gif"/></a></div></td></tr>';
			}
			pan_html += '</table>';
		} else {
			pan_html += '<div class="panel panel-default subpanel"><div id="heading' + convertToSlug(data[c].name) + '" class="panel-heading" role="tab" data-toggle="collapse" data-parent="#category' + tag + '" href="#' + convertToSlug(data[c].name) + '" aria-expanded="true" aria-controls="' + convertToSlug(data[c].name) + '"><h3 class="panel-title"><span class="icon glyphicon glyphicon-chevron-right" aria-hidden="true"></span>&nbsp;&nbsp;<span>' + data[c].name + '</span></h3></div><div id="' + convertToSlug(data[c].name) + '" class="panel-collapse collapse" role="tabpanel" aria-labelledby="heading' + convertToSlug(data[c].name) + '"><div class="panel-body"><table class="table table-hover table-striped"><tr><th class="col-md-2"></th><th class="col-md-2"></th><th class="col-md-5"></th><th class="col-md-3"></th></tr>';

			if (data[c].SS_entry.length) {
				for (e in data[c].SS_entry) {
					pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/repository/detail/' + data[c].SS_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].SS_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Standard State</span></p><i>Version:</i> <mark>' + data[c].SS_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].SS_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].SS_entry[e].data_count + '</code></p></td><td><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].SS_entry[e].authors + '</i>. <b>' + data[c].SS_entry[e].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].SS_entry[e].comments + '</p></td><td><a href="/repository/detail/' + data[c].SS_entry[e].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbs/' + data[c].SS_entry[e].cid + '/' + convertToSlug(data[c].name) + '.gif"/></a></td></tr>';
				}
			}
			if (data[c].TT_entry.length) {
				for (e in data[c].TT_entry) {
					pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/repository/detail/' + data[c].TT_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].TT_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Titration</span></p><i>Version:</i> <mark>' + data[c].TT_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].TT_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].TT_entry[e].data_count + '</code></p></td><td><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].TT_entry[e].authors + '</i>. <b>' + data[c].TT_entry[e].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].TT_entry[e].comments + '</p></td><td><a href="/repository/detail/' + data[c].TT_entry[e].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbs/' + data[c].TT_entry[e].cid + '/' + convertToSlug(data[c].name) + '.gif"/></a></td></tr>';
				}
			}
			if (data[c].MM_entry.length) {
				for (e in data[c].MM_entry) {
					pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/repository/detail/' + data[c].MM_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].MM_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Mutate and Map</span></p><i>Version:</i> <mark>' + data[c].MM_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].MM_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].MM_entry[e].data_count + '</code></p></td><td><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].MM_entry[e].authors + '</i>. <b>' + data[c].MM_entry[e].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].MM_entry[e].comments + '</p></td><td><a href="/repository/detail/' + data[c].MM_entry[e].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbs/' + data[c].MM_entry[e].cid + '/' + convertToSlug(data[c].name) + '.gif"/></a></td></tr>';
				}
			}
			if (data[c].MA_entry.length) {
				for (e in data[c].MA_entry) {
					pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/repository/detail/' + data[c].MA_entry[e].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].MA_entry[e].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">MOHCA</span></p><i>Version:</i> <mark>' + data[c].MA_entry[e].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].MA_entry[e].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].MA_entry[e].data_count + '</code></p></td><td><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].MA_entry[e].authors + '</i>. <b>' + data[c].MA_entry[e].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].MA_entry[e].comments + '</p></td><td><a href="/repository/detail/' + data[c].MA_entry[e].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbs/' + data[c].MA_entry[e].cid + '/' + convertToSlug(data[c].name) + '.gif"/></a></td></tr>';
				}
			}
			pan_html += '</table></div></div></div>';
		}
	}
	pan_html += '</table>';
	return pan_html;
}

function fill_category_thumb(data, tag) {
	var pan_html = '';
	for (c in data) {
		if (tag == "Eterna") {
			for (e in data[c].SS_entry) {
				pan_html += '<div class="panel panel-default subpanel eterna-panel"><div id="heading' + convertToSlug(data[c].SS_entry[e].rmdb_id) + '" class="panel-heading" role="tab" data-toggle="collapse" data-parent="#category' + tag + '" href="#' + convertToSlug(data[c].SS_entry[e].rmdb_id) + '" aria-expanded="true" aria-controls="' + convertToSlug(data[c].SS_entry[e].rmdb_id) + '"><div class="panel-title" ><span class="icon glyphicon glyphicon-chevron-right" aria-hidden="true"></span>&nbsp;&nbsp;<span class="label label-default" style="font-size:16px;">' + colorEternaId(data[c].SS_entry[e].rmdb_id) + '</span></div></div><div id="'+ convertToSlug(data[c].SS_entry[e].rmdb_id) + '" class="panel-collapse collapse eterna-subpanel" role="tabpanel" aria-labelledby="heading'+ convertToSlug(data[c].SS_entry[e].rmdb_id) + '"><div class="panel-body"><a href="/repository/detail/'+ data[c].SS_entry[e].rmdb_id + '" class="row browse-rotate thumbnail pull-left" style="left:-200px;"><img src="/site_data/thumbs/' + data[c].SS_entry[e].cid + '/'  + convertToSlug(data[c].name) + '.gif"/></a></div></div></div>';
			}
		} else {
			pan_html += '<div class="panel panel-default subpanel"><div id="heading' + convertToSlug(data[c].name) + '" class="panel-heading" role="tab" data-toggle="collapse" data-parent="#category' + tag + '" href="#' + convertToSlug(data[c].name) + '" aria-expanded="true" aria-controls="' + convertToSlug(data[c].name) + '"><h3 class="panel-title"><span class="icon glyphicon glyphicon-chevron-right" aria-hidden="true"></span>&nbsp;&nbsp;<span>' + data[c].name + '</span></h3></div><div id="' + convertToSlug(data[c].name) + '" class="panel-collapse collapse" role="tabpanel" aria-labelledby="heading' + convertToSlug(data[c].name) + '"><div class="panel-body"><ul>';

			if (data[c].SS_entry.length) {
				pan_html += '<li><h3><span class="label label-primary">Standard State</span></h3></li><div class="row">';
				for (e in data[c].SS_entry) {
					pan_html += '<div class="col-md-4 entry-list"><a href="/repository/detail/' + data[c].SS_entry[e].rmdb_id + '" class="thumbnail"><p class="lead" style="padding-top:10px;"><span class="label label-default">' + colorRmdbId(data[c].SS_entry[e].rmdb_id) + '</span></p><img src="/site_data/thumbs/' + data[c].SS_entry[e].cid + '/'  + convertToSlug(data[c].name) + '.gif"/></a></div>';
				}
				pan_html += '</div>';
			}
			if (data[c].TT_entry.length) {
				pan_html += '<li><h3><span class="label label-info">Titration</span></h3></li><div class="row">';
				for (e in data[c].TT_entry) {
					pan_html += '<div class="col-md-4 entry-list"><a href="/repository/detail/' + data[c].TT_entry[e].rmdb_id + '" class="thumbnail"><p class="lead" style="padding-top:10px;"><span class="label label-default">' + colorRmdbId(data[c].TT_entry[e].rmdb_id) + '</span></p><img src="/site_data/thumbs/' + data[c].TT_entry[e].cid + '/'  + convertToSlug(data[c].name) + '.gif"/></a></div>';
				}
				pan_html += '</div>';
			}
			if (data[c].MM_entry.length) {
				pan_html += '<li><h3><span class="label label-success">Mutate and Map</span></h3></li><div class="row">';
				for (e in data[c].MM_entry) {
					pan_html += '<div class="col-md-4 entry-list"><a href="/repository/detail/' + data[c].MM_entry[e].rmdb_id + '" class="thumbnail"><p class="lead" style="padding-top:10px;"><span class="label label-default">' + colorRmdbId(data[c].MM_entry[e].rmdb_id) + '</span></p><img src="/site_data/thumbs/' + data[c].MM_entry[e].cid + '/'  + convertToSlug(data[c].name) + '.gif"/></a></div>';
				}
				pan_html += '</div>';
			}
			if (data[c].MA_entry.length) {
				pan_html += '<li><h3><span class="label label-danger">MOHCA</span></h3></li><div class="row">';
				for (e in data[c].MA_entry) {
					pan_html += '<div class="col-md-4 entry-list"><a href="/repository/detail/' + data[c].MA_entry[e].rmdb_id + '" class="thumbnail"><p class="lead" style="padding-top:10px;"><span class="label label-default">' + colorRmdbId(data[c].MA_entry[e].rmdb_id) + '</span></p><img src="/site_data/thumbs/' + data[c].MA_entry[e].cid + '/'  + convertToSlug(data[c].name) + '.gif"/></a></div>';
				}
				pan_html += '</div>';
			}
			pan_html += '</ul></div></div></div>';			
		}
	}	
	return pan_html;
}


$(document).ready(function() {
	$(".dropdown-toggle").removeClass("active");
	$("#nav_browse").addClass("active");
	$("#nav_logo").css("text-decoration","none");

	$("#sidebar").css("width", $("#sidebar").width());
	$("#sidebar").affix({offset: {top: $("#main").position().top} });	

	$.ajax({
		url: '/repository/api/index/stats/',
		dataType: 'json',
		async: true,
		success: function(data) {
			$("#N_all").text(data.N_all);
			$("#N_general").text(data.N_all - data.N_puzzle - data.N_eterna);
			$("#N_puzzle").text(data.N_puzzle);
			$("#N_eterna").text(data.N_eterna);
		},
		complete: function(xhr) {
			$.ajax({
				url: '/repository/api/index/browse/general',
				dataType: 'json',
				async: true,
				success: function(data) { 
					json_general = data;
					$("#panel_general").html(fill_category_thumb(json_general, 'General')); 
					$("#categoryGeneral").find(".panel-body>.subpanel:first>.panel-collapse").collapse("show");
					$("#categoryGeneral").find(".panel-body>.subpanel:first>.panel-collapse").siblings().find(".panel-title>.icon")
						.removeClass("glyphicon-chevron-right")
						.addClass("glyphicon-chevron-down");
				},
				complete: function(xhr) {
					$.ajax({
						url: '/repository/api/index/browse/puzzle',
						dataType: 'json',
						async: true,
						success: function(data) { 
							json_puzzle = data;
							$("#panel_puzzle").html(fill_category_thumb(json_puzzle, 'Puzzle')); 
							$("#categoryPuzzle").find(".panel-body>.subpanel:first>.panel-collapse").collapse("show");
							$("#categoryPuzzle").find(".panel-body>.subpanel:first>.panel-collapse").siblings().find(".panel-title>.icon")
								.removeClass("glyphicon-chevron-right")
								.addClass("glyphicon-chevron-down");
						},
						complete: function(xhr) {
							$.ajax({
								url: '/repository/api/index/browse/eterna',
								dataType: 'json',
								async: true,
								success: function(data) { 
									json_eterna = data;
									$("#panel_eterna").html(fill_category_thumb(json_eterna, 'Eterna')); 
									$("#categoryEteRNA").find(".panel-body>.subpanel:first>.panel-collapse").collapse("show");
									$("#categoryEteRNA").find(".panel-body>.subpanel:first>.panel-collapse").siblings().find(".panel-title>.icon")
										.removeClass("glyphicon-chevron-right")
										.addClass("glyphicon-chevron-down");
								},
								complete: function(xhr) {
									$('.panel-collapse').on('show.bs.collapse', function () {
										$(this).siblings().find(".panel-title>.icon")
											.removeClass("glyphicon-chevron-right")
											.addClass("glyphicon-chevron-down");
									});
									$('.panel-collapse').on('hidden.bs.collapse', function () {
										$(this).siblings().find(".panel-title>.icon")
											.removeClass("glyphicon-chevron-down")
											.addClass("glyphicon-chevron-right");
									});
								}
							});
						}
					});
				}
			});
		}
	});


	$("#buttonAll, #buttonGeneral, #buttonPuzzle, #buttonEteRNA").on("click", function () {
		$("#categoryGeneral, #categoryPuzzle, #categoryEteRNA").hide();
		$("#buttonAll, #buttonGeneral, #buttonPuzzle, #buttonEteRNA").removeClass("active");
	});
	$("#buttonAll").on("click", function () {
		$("#categoryGeneral, #categoryPuzzle, #categoryEteRNA").show();
		$("#buttonAll").addClass("active");
	    $('html, body').stop().animate({scrollTop: 0}, 500);
	});
	$("#buttonGeneral").on("click", function () {
		$("#categoryGeneral").show();
		$("#buttonGeneral").addClass("active");
	    $('html, body').stop().animate({scrollTop: 0}, 500);
	});
	$("#buttonPuzzle").on("click", function () {
		$("#categoryPuzzle").show();
		$("#buttonPuzzle").addClass("active");
	    $('html, body').stop().animate({scrollTop: 0}, 500);
	});
	$("#buttonEteRNA").on("click", function () {
		$("#categoryEteRNA").show();
		$("#buttonEteRNA").addClass("active");
	    $('html, body').stop().animate({scrollTop: 0}, 500);
	});

	$("#view_list, #view_thumb").on("click", function() {$(window).unbind();});

	$("input:radio").on("change", function () {
		$("#wait").fadeIn();
		$("#panel_general").html(''); 
		$("#panel_puzzle").html(''); 
		$("#panel_eterna").html(''); 
		if ($(this).val() == "thumb") {
			$("#panel_general").html(fill_category_thumb(json_general, 'General')); 
			$("#panel_puzzle").html(fill_category_thumb(json_puzzle, 'Puzzle')); 
			$("#panel_eterna").html(fill_category_thumb(json_eterna, 'Eterna')); 
		} else {
			$("#panel_general").html(fill_category_list(json_general, 'General')); 
			$("#panel_puzzle").html(fill_category_list(json_puzzle, 'Puzzle')); 
			console.log(json_puzzle[0]);
			console.log(json_puzzle[1]);
			$("#panel_eterna").html(fill_category_list(json_eterna, 'Eterna')); 
		}

		$(".category").each(function () {
			$(this).find(".panel-body>.subpanel:first>.panel-collapse").collapse("show");
			$(this).find(".panel-body>.subpanel:first>.panel-collapse").siblings().find(".panel-title>.icon")
				.removeClass("glyphicon-chevron-right")
				.addClass("glyphicon-chevron-down");
		});
		$("#wait").fadeOut();

		$('.panel-collapse').on('show.bs.collapse', function () {
			$(this).siblings().find(".panel-title>.icon")
				.removeClass("glyphicon-chevron-right")
				.addClass("glyphicon-chevron-down");
		});
		$('.panel-collapse').on('hidden.bs.collapse', function () {
			$(this).siblings().find(".panel-title>.icon")
				.removeClass("glyphicon-chevron-down")
				.addClass("glyphicon-chevron-right");
		});
	});

});