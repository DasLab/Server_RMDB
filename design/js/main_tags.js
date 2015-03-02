function wbr(str) {  
	return str.match(/.{1,40}/g);
}

function show_tag_ann(tag_idx) {
	$(".tag-browse").remove();

	var i = tags.data_annotation[tag_idx];
	var tag_html = '<tr class="tag-temp tag-browse"><td class="text-right"><b><i><u>' + (parseInt(tag_idx)+1) + '</u></i></b></td>';

	var data_ann_idx = 0;
	for (j in i) {
		if (data_ann_idx==0) {
			tag_html += '<td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
		} else {
			tag_html += '<tr class="tag-temp tag-browse"><td></td><td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
		}
		for (k in i[j]) {
			if (k!=i[j].length-1) { tag_html += '<p style=\"padding-bottom:5px;\">'; }
			if (j.toUpperCase()=='SEQUENCE' | j.toUpperCase()=='STRUCTURE') { 
				var seq_tmp = wbr(i[j][k]);
				for (l in seq_tmp) {
					tag_html += '<p style=\"padding-bottom:5px;\"><samp><span class=\"label label-warning\">' + seq_tmp[l] + '</span></samp></p>';
				}
			} else {
				tag_html += '<span class=\"label label-warning\">' + i[j][k] + '</span>';
			}
			if (k!=i[j].length-1) { tag_html += '</p>'; }
		}
		tag_html += '</td></tr>';
		data_ann_idx += 1;
	}
	$(tag_html).insertAfter(".tag-temp");
}

function fill_tags() {
	$("#tag_name_panel").text(tags.name);
	$("#tag_name_main").text(tags.name);

	$("#tag_comments").text(tags.comments);
	$("#tag_sequence_len").html("<code>1-by-" + tags.sequence_len + "</code> <i>vector</i>");
	$("#tag_structure_len").html("<code>1-by-" + tags.structure_len + "</code> <i>vector</i>");
	$("#tag_seqpos").html("<p>" + tags.seqpos + "</p><code>1-by-" + tags.seqpos_len + "</code> <i>vector</i>");
	$("#tag_offset").html("<code>" + tags.offset + "</code>");
	$("#tag_data").html("<code>" + tags.data_nrow + "-by-" + tags.data_ncol + "</code> <i>matrix</i>");
	if (tags.err_ncol) {
		$("#tag_data_err").html("<code>" + tags.data_nrow + "-by-" + tags.err_ncol + "</code> <i>matrix</i>");
	} else {
		$("#tag_data_err").html("<code>N/A</code> (not available)");
	}
	if (tags.xsel_len) {
		$("#tag_xsel").html("<code>1-by-" + tags.xsel_len + "</code> <i>vector</i>");
	} else {
		$("#tag_xsel").html("<code>N/A</code> (not available)");
	}
	$("#tag_rdat_ver").html("<code>" + tags.rdat_ver + "</code>");
	$("#tag_version").text(tags.version);
	$("#tag_n_construct").text(tags.construct_count);
	$("#tag_n_data").text(tags.data_count);
	$("#tag_creation_date").text(tags.creation_date);
	$("#tag_rev_stat").html(tags.revision_status_label);
	$("#tag_owner").html("<b>" + tags.owner_name + "</b> <kbd>" + tags.owner + "</kbd>");

	$("#tag_sequence").text(tags.sequence);
	$("#tag_structure").text(tags.structure);
	$("#tag_author").text(tags.authors);
	$("#tag_title").text(tags.pub_title);
	$("#tag_pubmed").text(tags.pubmed_id);
	$("#link_pubmed").attr("href", "http://www.ncbi.nlm.nih.gov/pubmed/" + tags.pubmed_id);
	$("#tag_description").text(tags.description);

	if (tags.pdb_ids) {
		var pdb_html = '';
		for (i in tags.pdb_ids) {
			pdb_html += '<a href="http://www.pdb.org/pdb/explore/explore.do?structureId=' + tags.pdb_ids[i] + '">' + tags.pdb_ids[i] + ' <span class="glyphicon glyphicon-new-window" aria-hidden="true"></span></a>, ';
		}
		$("#tag_pdb").html(pdb_html);
	} else {
		$("#tag_pdb").text('N/A');
	}

    var col_h = Math.max($("#panel_con").height(), $("#panel_cit").height()) + 15;
    $("#panel_con").css("height", col_h);
    $("#panel_cit").css("height", col_h);

    $("#tag_type").html(tags.type);
    var ann_html = '';
    for (i in tags.annotation) {
    	ann_html += '<tr><td></td><td class="lead text-right align-center"><span class="label label-danger">' + i + '</span></td><td class="lead">';
    	for (j in tags.annotation[i]) {
    		if (j==tags.annotation[i].length-1) {
	    		ann_html += '<span class=\"label label-warning\">' + tags.annotation[i][j] + '</span>';
    		} else {
	    		ann_html += '<p style=\"padding-bottom:5px;\"><span class=\"label label-warning\">' + tags.annotation[i][j] + '</span></p>';
    		}
    	}
    	ann_html += '</td></tr>'
    }
    $(ann_html).insertAfter("#tag_annotation");

    var dat_ann_html = '';
    if (tags.type.indexOf('MOHCA')!=-1 | tags.name.indexOf('EteRNA')!=-1) {

	    $("#tag_data_switch").html('<button id="tag_ann_switch" class="btn btn-default all"><span class="glyphicon glyphicon-sort" aria-hidden="true"></span> Show All</button>');
    	$("#tag_ann_switch").bind("click", function() {
    		$(".tag-temp").remove();
    		if ($(this).hasClass("all")) {
    			$(this).html('<span class="glyphicon glyphicon-sort" aria-hidden="true"></span> Show All').removeClass("all");

			    dat_ann_html = '<tr class="tag-temp"><td class="pull-right"><span class="btn-group" role="group"><button id="tag_ann_top" class="btn btn-default">&nbsp;<span class="glyphicon glyphicon-fast-backward" aria-hidden="true"></span>&nbsp;</button><button id="tag_ann_up" class="btn btn-default"><span class="glyphicon glyphicon-backward" aria-hidden="true"></span>&nbsp;</button></span></td><td><input type="text" class="form-control" id="tag_ann_num" style="text-align: center;"/></td><td><span class="btn-group" role="group"><button id="tag_ann_down" class="btn btn-default">&nbsp;<span class="glyphicon glyphicon-forward" aria-hidden="true"></span></button><button id="tag_ann_bottom" class="btn btn-default">&nbsp;<span class="glyphicon glyphicon-fast-forward" aria-hidden="true"></span>&nbsp;</button></span></td>';
				$(dat_ann_html).insertAfter("#tag_data_annotation");

				$("#tag_ann_top").bind("click", function() {
					tag_idx = 0;
					show_tag_ann(tag_idx);
				    $("#tag_ann_num").val((tag_idx+1).toString());
				});
				$("#tag_ann_bottom").bind("click", function() {
					tag_idx = n_rows-1;
					show_tag_ann(tag_idx);
				    $("#tag_ann_num").val((tag_idx+1).toString());
				});
				$("#tag_ann_up").bind("click", function() {
					if (tag_idx > 0) {
						tag_idx -= 1;
						show_tag_ann(tag_idx);
					}
				    $("#tag_ann_num").val((tag_idx+1).toString());
				});
				$("#tag_ann_down").bind("click", function() {
					if (tag_idx < n_rows-1) {
						tag_idx += 1;
						show_tag_ann(tag_idx);
					}
				    $("#tag_ann_num").val((tag_idx+1).toString());
				});
				$("#tag_ann_num").bind("focusout", function () {
					var idx_tmp = parseInt($(this).val());
					if (!isNaN(idx_tmp)){
						if (idx_tmp < 0) {idx_tmp = 0;}
						if (idx_tmp > n_rows-1) {idx_tmp = n_rows-1;}
						tag_idx = idx_tmp-1;
						show_tag_ann(tag_idx);
					    $("#tag_ann_num").val((tag_idx+1).toString());
					}
				});
				$("#tag_ann_num").bind("keyup", function (e) {
					if(e.keyCode == 13) {$(this).trigger("focusout");}
				});
				$("#tag_ann_num").val((tag_idx+1).toString());
				$("#tag_ann_num").trigger("focusout");

    		} else {
    			dat_ann_html = '';
    			$(this).html('<span class="glyphicon glyphicon-sort" aria-hidden="true"></span> Select Only').addClass("all");
			    for (i in tags.data_annotation) {
			    	dat_ann_html += '<tr class="tag-temp"><td class="text-right"><b><i><u>' + (parseInt(i)+1) + '</u></i></b></td>';

			    	var data_ann_idx = 0;
					for (j in tags.data_annotation[i]) {
						if (data_ann_idx==0) {
							dat_ann_html += '<td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
						} else {
							dat_ann_html += '<tr class="tag-temp"><td></td><td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
						}
						for (k in tags.data_annotation[i][j]) {
							if (k!=tags.data_annotation[i][j].length-1) { dat_ann_html += '<p style=\"padding-bottom:5px;\">'; }
							if (j.toUpperCase()=='SEQUENCE' | j.toUpperCase()=='STRUCTURE') { 
								var seq_tmp = wbr(tags.data_annotation[i][j][k]);
								for (l in seq_tmp) {
									dat_ann_html += '<p style=\"padding-bottom:5px;\"><samp><span class=\"label label-warning\">' + seq_tmp[l] + '</span></sa,p></p>';
								}
							} else {
								dat_ann_html += '<span class=\"label label-warning\">' + tags.data_annotation[i][j][k] + '</span>';
							}
							if (k!=tags.data_annotation[i][j].length-1) { dat_ann_html += '</p>'; }
						}
						dat_ann_html += '</td></tr>';
						data_ann_idx += 1;
					}
			    }
				$(dat_ann_html).insertAfter("#tag_data_annotation");
    		}
    	})
	    $("#tag_ann_switch").trigger("click");

    } else {
	    for (i in tags.data_annotation) {
	    	dat_ann_html += '<tr><td class="text-right"><b><i><u>' + (parseInt(i)+1) + '</u></i></b></td>';

	    	var data_ann_idx = 0;
			for (j in tags.data_annotation[i]) {
				if (data_ann_idx==0) {
					dat_ann_html += '<td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
				} else {
					dat_ann_html += '<tr><td></td><td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
				}
				for (k in tags.data_annotation[i][j]) {
					if (k==tags.data_annotation[i][j].length-1) {
			    		dat_ann_html += '<span class=\"label label-warning\">' + tags.data_annotation[i][j][k] + '</span>';
					} else {
			    		dat_ann_html += '<p style=\"padding-bottom:5px;\"><span class=\"label label-warning\">' + tags.data_annotation[i][j][k] + '</span></p>';
					}
				}
				dat_ann_html += '</td></tr>';
				data_ann_idx += 1;
			}
	    }
		$(dat_ann_html).insertAfter("#tag_data_annotation");
    }

}



