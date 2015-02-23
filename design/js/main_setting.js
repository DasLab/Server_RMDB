$(document).ready(function() {
    $("#show_seq").on("click", function() {
        if ($(this).is(':checked')) {
            d3.select("#seq_overlay").classed("shown", true);
        } else {
            d3.select("#seq_overlay").classed("shown", false);
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

    $("#color_text").attr("min",0).attr("max",3).attr("step",0.2).val(1);
    $("#color_slide").attr("min",0).attr("max",3).attr("step",0.2).val(1);
    $("#color_text").on("change", function() {
        $("#color_slide").val($("#color_text").val());
    });
    $("#color_slide").on("change", function() {
        $("#color_text").val($("#color_slide").val());
        
        color_scale = $("#color_slide").val();
        var colorScale = d3.scale.linear()
                        .domain([json.peak_min, json.peak_mean + color_scale*json.peak_sd])
                        .range(['white', 'black']);
        d3.select("#heat_map").selectAll("rect.tile").style("fill", function(d) { return colorScale(d.value); });
    });


});
