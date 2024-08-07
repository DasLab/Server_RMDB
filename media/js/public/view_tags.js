function wbr(str) {  
    return str.match(/.{1,80}/g);
}

function show_tag_ann(tag_idx) {
    $(".tag-browse").remove();

    var i = tags.data_annotation[tag_idx];
    var tag_html = '<tr class="tag-temp tag-browse"><td class="text-right"><b><i><u>' + (parseInt(tag_idx) + 1) + '</u></i></b></td>';

    var data_ann_idx = 0;
    for (var j in i) {
        if (data_ann_idx === 0) {
            tag_html += '<td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
        } else {
            tag_html += '<tr class="tag-temp tag-browse"><td></td><td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
        }
        for (var k = 0; k < i[j].length; k++) {
            if (k != i[j].length - 1) { tag_html += '<p style="padding-bottom:5px;">'; }
            if (j.toUpperCase() === 'SEQUENCE' | j.toUpperCase() === 'STRUCTURE') { 
                var seq_tmp = wbr(i[j][k]);
                // Enumerate an array
                for (var l = 0; l < seq_tmp.length; l++) {
                    tag_html += '<p style="padding-bottom:5px;"><samp><span class="label label-warning">' + seq_tmp[l] + '</span></samp></p>';
                }
            } else {
                tag_html += '<span class="label label-warning">' + i[j][k] + '</span>';
            }
            if (k != i[j].length - 1) { tag_html += '</p>'; }
        }
        tag_html += '</td></tr>';
        data_ann_idx += 1;
    }
    $(tag_html).insertAfter("#tag_barplot");
    $("#img_panel").css("height", Math.min( parseInt($("#tag_browse").css("height")) + parseInt($("#svg_parent").css("height")) + 25, $(window).height() - parseInt($(".navbar-fixed-top").css("height"))));
    $("#img_panel").css("top", $(window).height() - parseInt($("#img_panel").css("height")));
    $("#img-buttons").css("margin-top", parseInt($("#left-buttons").css("height")) + parseInt($("#left-buttons").css("margin-top")) - parseInt($("#img_panel").css("top")) + parseInt($(".navbar-fixed-top").css("height")) - 1);
}

function fill_tags() {
    $("#tag_name_panel").text(tags.name);
    $("#tag_name_main").text(tags.name);

    $("#tag_comments").html('<p class="excerpt">' + tags.comments.replace(/\n/g, '<br/>') + '</p>');
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
    $("#tag_rev_stat").html(render_status(tags.status));
    $("#tag_owner").html("<b>" + tags.owner_name + "</b> <kbd>" + tags.owner + "</kbd>");

    $("#tag_sequence").text(tags.sequence);
    $("#tag_structure").text(tags.structure);
    $("#tag_author").text(tags.authors);
    $("#tag_title").text(tags.pub_title);
    if(/^\d+$/.test(tags.pubmed_id)) {
        $("#tag_pubmed").text(tags.pubmed_id);
        $("#link_pubmed").attr("href", "http://www.ncbi.nlm.nih.gov/pubmed/" + tags.pubmed_id);
        $("#link_relatedEntries").attr("href", "/browse/table?pubmed_id=" + tags.pubmed_id);
    }else{
        $("#link_pubmed").css("display", "none");
        $("#show_publication").css("display", "none");
    }

    var tags_description = tags.description.trim();
    if(tags_description){
        $("#tag_description").text(tags_description);
    }else{
        $("#show_description").css("display", "none");
    }


    $("#img_prv").attr("src", "/site_data/image/" + rmdb_id + "-rx.png");
    $("#dl_isatab").attr("href", "/site_data/file/" + tags.rmdb_id + "/" + tags.rmdb_id + "_" + tags.version + ".xls");
    $("#dl_rdat").attr("href", "/site_data/file/" + tags.rmdb_id + "/" + tags.rmdb_id + ".rdat");
    if (tags.version > 1) {
        var ver_html = '<li class="li-orange"><a href="/site_data/file/' + tags.rmdb_id + '/' + tags.rmdb_id + '_' + tags.version + '.rdat" download><span class="glyphicon glyphicon-compressed" aria-hidden="true"></span>&nbsp;&nbsp;(Current) <i>Version:</i> <mark>' + tags.version + '</mark></a></li>';
        for (var i = tags.versions.length - 1; i >= 0; i--) {
            if (tags.versions[i] !== tags.version) {
                ver_html += '<li class="li-info"><a href="/site_data/file/' + tags.rmdb_id + '/' + tags.rmdb_id + '_' + i + '.rdat" download><span class="glyphicon glyphicon-compressed" aria-hidden="true"></span>&nbsp;&nbsp;RDAT <i>Version:</i> <mark>' + i + '</mark></a></li>';
            }
        }
        $("#hist_ver_list").html(ver_html);
    } else {
        $("#hist_ver_btn").hide();
    }
    if (tags.latest) {
        $("#tag_supercede").html('<button type="button" class="btn btn-danger dropdown-toggle" data-toggle="dropdown" aria-expanded="false"><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>&nbsp;&nbsp;Superceded&nbsp;<span class="caret"></span></button><ul class="dropdown-menu nav nav-pills nav-stacked" role="menu"><li class="li-green"><a href="/detail/' + tags.latest + '"><span class="glyphicon glyphicon-thumbs-up" aria-hidden="true"></span>&nbsp;&nbsp;' + tags.latest + '</a></li></ul>');
    } else {
        $("#tag_supercede").html('<button type="button" class="btn btn-success dropdown-toggle" data-toggle="dropdown" aria-expanded="false"><span class="glyphicon glyphicon-ok-sign" aria-hidden="true"></span>&nbsp;&nbsp;Latest&nbsp;</button>');
    }

    if (tags.pdb_ids.length > 0) {
        var pdb_html = '';
        for (var i in tags.pdb_ids) {
            pdb_html += '<a href="http://www.pdb.org/pdb/explore/explore.do?structureId=' + tags.pdb_ids[i] + '">' + tags.pdb_ids[i] + ' <span class="glyphicon glyphicon-new-window" aria-hidden="true"></span></a>, ';
        }
        $("#tag_pdb").html(pdb_html);
    } else {
        $("#show_pdb").css("display", "none");
    }

    var col_h = Math.max(parseInt($("#panel_con").css("height")), parseInt($("#panel_cit").css("height")));
    $("#panel_con").css("height", col_h);
    $("#panel_cit").css("height", col_h);

    $("#tag_type").html(render_type(tags.type));
    var ann_html = '';
    for (var i in tags.annotation) {
        ann_html += '<tr><td></td><td class="lead text-right align-center"><span class="label label-danger">' + i + '</span></td><td class="lead">';
        for (var j in tags.annotation[i]) {
            var prefix = (j != tags.annotation[i].length - 1 ? '<p style="padding-bottom:5px;">' : ''),
                suffix = (j != tags.annotation[i].length - 1 ? '</p>' : '');
            ann_html += prefix + '<span class="label label-warning">' + tags.annotation[i][j] + '</span>' + suffix;
        }
        ann_html += '</td></tr>';
    }
    $(ann_html).insertAfter("#tag_annotation");

    var dat_ann_html = '';
    if (tags.type.indexOf('MOHCA') !== -1 | tags.name.indexOf('EteRNA') !== -1) {

        $("#tag_data_switch").html('<button id="tag_ann_switch" class="btn btn-default"><span class="glyphicon glyphicon-sort" aria-hidden="true"></span> Show All</button>');
        $("#tag_ann_switch").bind("click", function() {
            dat_ann_html = '';
            $(this).fadeOut();
            for (var i in tags.data_annotation) {
                dat_ann_html += '<tr class="tag-temp"><td class="text-right"><b><i><u>' + (parseInt(i) + 1) + '</u></i></b></td>';

                var data_ann_idx = 0;
                for (var j in tags.data_annotation[i]) {
                    if (data_ann_idx === 0) {
                        dat_ann_html += '<td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
                    } else {
                        dat_ann_html += '<tr class="tag-temp"><td></td><td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
                    }
                    for (var k in tags.data_annotation[i][j]) {
                        if (k != tags.data_annotation[i][j].length - 1) { dat_ann_html += '<p style="padding-bottom:5px;">'; }
                        var label_class = (j === 'datatype' ? 'success' : 'warning');

                        if (j.toUpperCase() === 'SEQUENCE' | j.toUpperCase() === 'STRUCTURE') {
                            var seq_tmp = wbr(tags.data_annotation[i][j][k]);
                            for (var l in seq_tmp) {
                                dat_ann_html += '<p style="padding-bottom:5px;"><samp><span class="label label-' + label_class + '">' + seq_tmp[l] + '</span></samp></p>';
                            }
                        } else {
                            dat_ann_html += '<span class="label label-' + label_class + '">' + tags.data_annotation[i][j][k] + '</span>';
                        }
                        if (k != tags.data_annotation[i][j].length - 1) { dat_ann_html += '</p>'; }
                    }
                    dat_ann_html += '</td></tr>';
                    data_ann_idx += 1;
                }
            }
            $(dat_ann_html).insertAfter("#tag_data_annotation");
        });

    } else {
        for (var i in tags.data_annotation) {
            dat_ann_html += '<tr><td class="text-right"><b><i><u>' + (parseInt(i) + 1) + '</u></i></b></td>';

            var data_ann_idx = 0;
            for (var j in tags.data_annotation[i]) {
                if (data_ann_idx === 0) {
                    dat_ann_html += '<td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
                } else {
                    dat_ann_html += '<tr><td></td><td class="lead text-right align-center"><span class="label label-danger">' + j + '</span></td><td class="lead">';
                }
                for (var k in tags.data_annotation[i][j]) {
                    var label_class = (j === 'datatype' ? 'success' : 'warning');
                    if (k == tags.data_annotation[i][j].length - 1) {
                        dat_ann_html += '<span class="label label-' + label_class + '">' + tags.data_annotation[i][j][k] + '</span>';
                    } else {
                        dat_ann_html += '<p style="padding-bottom:5px;"><span class="label label-' + label_class + '">' + tags.data_annotation[i][j][k] + '</span></p>';
                    }
                }
                dat_ann_html += '</td></tr>';
                data_ann_idx += 1;
            }
        }
        $(dat_ann_html).insertAfter("#tag_data_annotation");
    }

}

/**
 * Load the reactivity data from the json file and feed it to the selector.
 *
 * It also need the "annotation" data when doing the prep.
 *
 * @param data_sets
 * @param annotation_sets
 */
function load_reactivity_data(reactivity_sets, annotation_sets) {

    var select = $('#tag_reactivity_sets');

    // Check if need to show the RNA structure.
    if (reactivity_sets === undefined || Object.keys(reactivity_sets).length === 0) {
        $('#rna_structure_panel').hide();
        return;
    }

    //
    if(select.prop) {
      var options = select.prop('options');
    }
    else {
      var options = select.attr('options');
    }

    // Remove the current options.
    $('option', select).remove();
    for(var index in reactivity_sets) {
        var annotation = null;
        if (annotation_sets.hasOwnProperty(index - 1)) {  // Reactivity data array start with "1" while Annotation data starts with "0"
            var modifier_array = annotation_sets[index - 1]['modifier'];
            if (Array.isArray(modifier_array)) {
                annotation = annotation_sets[index - 1]['modifier'].join('-');
            }
        }

        // For the "value" of the selector, add the "modifier" annotation info if available.
		options[options.length] = new Option(annotation === null? index : index + '-' + annotation, reactivity_sets[index].join(' '));
	}

    // Make the "first" option selected
    select.find('option:eq(0)').prop('selected', true);
    // Load the RNA structure based on the selection
    load_rna_structure();
}

/**
 * Load RNA structure based on the reactivity data set selection.
 */
function load_rna_structure() {
    var select = $('#tag_reactivity_sets');

    if (select.val() === null) {
        return;
    }

    var reactivity = [];
    reactivity = select.val().split(' ').map(Number).filter(Boolean);
    var maxReactvity = Math.max.apply(null, reactivity);
    var minReactvity = Math.min.apply(null, reactivity);

    var container = new fornac.FornaContainer("#rna-structure", {
        'applyForce': true,
        'allowPanningAndZooming': true,
        'initialSize':[600, 600]
    });

    var options = {
        'structure': tags.structure, // from "tags" json data.
        'sequence': tags.sequence
    };

    var index = $('#tag_reactivity_sets :selected').html().split("-")[0];
    var annotation_sets = tags.data_annotation;
    if (annotation_sets.hasOwnProperty(index - 1)) {  // Reactivity data array start with "1" while Annotation data starts with "0"
            var selected_set = annotation_sets[index - 1];
            if (selected_set.hasOwnProperty('structure')) {
                options.structure = selected_set.structure[0];
            }
            if (selected_set.hasOwnProperty('sequence')) {
                options.sequence = selected_set.sequence[0];
            }
        }

    // Add RNA Structure
    container.addRNA(options.structure, options);
    // Add coloring data - reactivity data
    // NOTE: each of the reactivities is joint by `space`.
    container.addCustomColorsText(select.val(), minReactvity, maxReactvity);
}
