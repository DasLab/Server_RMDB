
function fill_category_list(data, tag) {
	if (tag == "Eterna") {
		var pan_html = '<table class="table table-hover table-striped"><tr><th class="col-md-2"></th><th class="col-md-2"></th><th class="col-md-8"></th></tr>';
		for (c in data) {
			pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/detail/' + data[c].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Standard State</span></p><i>Version:</i> <mark>' + data[c].version + '</mark><br/><i># of Construct:</i> <code>' + data[c].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].data_count + '</code></p></td><td id="' + data[c].rmdb_id + '" class="eterna-subpanel"><div style="height:220px;overflow:hidden;"><a href="/detail/' + data[c].rmdb_id + '" class="row browse-rotate thumbnail pull-left" style="left:-300px;"><img src="/site_data/thumbs/' + data[c].cid + '.gif"/></a></div></td></tr>';
		}
	} else {
		var pan_html = '<table class="table table-hover table-striped"><tr><th class="col-md-2"></th><th class="col-md-2"></th><th class="col-md-5"></th><th class="col-md-3"></th></tr>';
		for (c in data) {
			pan_html += '<tr><td class="text-right"><p class="lead"><span class="label label-default" style="background:#000;">RMDB_ID</span></p><p class="lead"><span class="label label-danger">experimentType</span></p><p class="lead"><span class="label label-violet">Stats</span></p></td><td><p class="lead"><a href="/detail/' + data[c].rmdb_id + '"><span class="label label-default">' + colorRmdbId(data[c].rmdb_id) + '</span></a></p><p class="lead"><span class="label label-success">Standard State</span></p><i>Version:</i> <mark>' + data[c].version + '</mark><br/><i># of Construct:</i> <code>'+ data[c].construct_count + '</code><br/><i># of Data point:</i> <code>' + data[c].data_count + '</code></p></td><td><p><span class="lead"><span class="label label-brown">Publication</span></span></p><p><i>' + data[c].authors + '</i>. <b>' + data[c].title + '</b>.</p><p><span class="lead"><span class="label label-primary">COMMENT</span></span></p><p class="excerpt">' + data[c].comments + '</p></td><td><a href="/detail/' + data[c].rmdb_id + '" class="row thumbnail pull-left"><img src="/site_data/thumbs/' + data[c].cid + '.gif"/></a></td></tr>';
		}
	}
	pan_html += '</table>';
	return pan_html;
}


$(document).ready(function() {
	$(".dropdown-toggle").removeClass("active");
	$("#nav_browse").addClass("active");
	$("#nav_logo").css("text-decoration","none");

	$("#sidebar").css("width", $("#sidebar").width());
	$("#sidebar").affix({
			offset: {
		  	top: $("#main").position().top
			}
	});	

	$("#buttonGeneral, #buttonEteRNA").on("click", function () {
		$('html, body').stop().animate({scrollTop: $($(this).attr("href")).offset().top - 75}, 500);
	});

	var search_word = $(location).attr("href").split("searchtext=")[1].replace('+','_');
	if (search_word.indexOf("#") != -1) {
		search_word = search_word.split("#")[0];
	}
	$.ajax({
		url: '/api/index/stats/',
		dataType: 'json',
		async: true,
		success: function(data) {
			$("#wait").fadeIn();
			$("#search_box").val(decodeURIComponent(search_word));
			$("#search_headline").text(decodeURIComponent(search_word));
			$("#N_all").text(data.N_all);
		},
		complete: function(xhr) {
			$.ajax({
				url: '/api/index/search/general/' + search_word,
				dataType: 'json',
				async: true,
				success: function(data) { 
					$("#panel_general").html(fill_category_list(data, 'General')); 
					if (data.length) {
						$("#N_search").html('<a id="buttonGeneral" href="#categoryGeneral" style="color:inherit"><span class="glyphicon glyphicon-heart" aria-hidden="true"></span>&nbsp;General # Entries</a>: <span class="badge" >' + data.length + '</span><br/>');
					}
				},
				complete: function(xhr) {
					$.ajax({
						url: '/api/index/search/eterna/' + search_word,
						dataType: 'json',
						async: true,
						success: function(data) { 
							$("#panel_eterna").html(fill_category_list(data, 'Eterna')); 
							if (data.length) {
								$("#N_search").html($("#N_search").html() + '<a id="buttonEteRNA" href="#categoryEteRNA" style="color:inherit"><span class="glyphicon glyphicon-cloud" aria-hidden="true"></span>&nbsp;EteRNA # Entries</a>: <span class="badge" >' + data.length + '</span><br/>');
							}
						},
						complete: function(xhr) {
							if(!$("#N_search").html().length) {
								$("#categoryGeneral").css("display", "none");
								$("#categoryEteRNA").css("display", "none");
								$("#categoryNA").css("display", "inline");
							}
							$("#wait").fadeOut();
						}
					});
				}
			});
		}
	});
});

