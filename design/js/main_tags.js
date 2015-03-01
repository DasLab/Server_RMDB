function fill_tags(json) {
	$("#tag_name_panel").text(json.name);
	$("#tag_name_main").text(json.name);

	$("#tag_comments").text(json.comments);
	$("#tag_sequence_len").html("<code>1-by-" + json.sequence_len + "</code> <i>vector</i>");
	$("#tag_structure_len").html("<code>1-by-" + json.structure_len + "</code> <i>vector</i>");
	$("#tag_seqpos").html("<p>" + json.seqpos + "</p><code>1-by-" + json.seqpos_len + "</code> <i>vector</i>");
	$("#tag_offset").html("<code>" + json.offset + "</code>");
	$("#tag_data").html("<code>" + json.data_nrow + "-by-" + json.data_ncol + "</code> <i>matrix</i>");
	if (json.err_ncol) {
		$("#tag_data_err").html("<code>" + json.data_nrow + "-by-" + json.err_ncol + "</code> <i>matrix</i>");
	} else {
		$("#tag_data_err").html("<code>N/A</code> (not available)");
	}
	if (json.xsel_len) {
		$("#tag_xsel").html("<code>1-by-" + json.xsel_len + "</code> <i>vector</i>");
	} else {
		$("#tag_xsel").html("<code>N/A</code> (not available)");
	}
	$("#tag_rdat_ver").html("<code>" + json.rdat_ver + "</code>");
	$("#tag_version").text(json.version);
	$("#tag_n_construct").text(json.construct_count);
	$("#tag_n_data").text(json.data_count);
	$("#tag_creation_date").text(json.creation_date);
	$("#tag_rev_stat").html(json.revision_status_label);

	$("#tag_sequence").text(json.sequence);
	$("#tag_structure").text(json.structure);
	$("#tag_author").text(json.authors);
	$("#tag_title").text(json.pub_title);
	$("#tag_pubmed").text(json.pubmed_id);
	$("#tag_description").text(json.description);

	if (json.pdb_ids) {
		var pdb_html = '';
		for (i in json.pdb_ids) {
			pdb_html += '<a href="http://www.pdb.org/pdb/explore/explore.do?structureId=' + json.pdb_ids[i] + '">' + json.pdb_ids[i] + ' <span class="glyphicon glyphicon-new-window" aria-hidden="true"></span></a>, '
		}
		$("#tag_pdb").html(pdb_html);
	} else {
		$("#tag_pdb").text('N/A');
	}

    var col_h = Math.max($("#panel_con").height(), $("#panel_cit").height()) + 15;
    $("#panel_con").css("height", col_h);
    $("#panel_cit").css("height", col_h);

    $("#tag_type").html(json.type);
    var ann_html = '';
    for (i in json.annotation) {
    	ann_html += '<tr><td></td><td class="lead text-right align-center"><span class="label label-danger">' + i + '</span></td><td class="lead">'
    	for (j in json.annotation[i]) {
    		if (j==json.annotation[i].length-1) {
	    		ann_html += '<span class=\"label label-warning\">' + json.annotation[i][j] + '</span>'
    		} else {
	    		ann_html += '<p style=\"padding-bottom:5px;\"><span class=\"label label-warning\">' + json.annotation[i][j] + '</span></p>'
    		}
    	}
    	ann_html += '</td></tr>'
    }
    $(ann_html).insertAfter("#tag_annotation");

    var dat_ann_html = '';
    for (i in json.data_annotation) {
    	dat_ann_html += '<tr><td class="text-right"><b><i><u>' + (parseInt(i)+1) + '</u></i></b></td>'

    	var data_ann_idx = 0;
		for (j in json.data_annotation[i]) {

			if (data_ann_idx==0) {
				dat_ann_html += '<td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">'
			} else {
				dat_ann_html += '<tr><td></td><td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">'
			}
			
			for (k in json.data_annotation[i][j]) {
				if (k==json.data_annotation[i][j].length-1) {
		    		dat_ann_html += '<span class=\"label label-warning\">' + json.data_annotation[i][j][k] + '</span>'
				} else {
		    		dat_ann_html += '<p style=\"padding-bottom:5px;\"><span class=\"label label-warning\">' + json.data_annotation[i][j][k] + '</span></p>'
				}
			}
			dat_ann_html += '</td></tr>'
			data_ann_idx += 1
		}
    }
    $(dat_ann_html).insertAfter("#tag_data_annotation");

    

}

