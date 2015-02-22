function seq_overlay(json) {
	var peaks = json.data;

    var overlayText = d3.select("#main").select("svg").append("g").selectAll("g")
						.data(peaks, function(d) { return d.y + ':' + d.x; }).enter()
						.append("text")
						.text(function(d) { return d.seq; })
						.attr("class", "overlay")
						.attr("y", function(d) { return (d.x+1) * (h+0.5) + main_margin.top -1; })
						.attr("x", function(d) { return d.y * (w+0.5) + main_margin.left +1; })
						.attr("fill", function(d) { return get_nt_color(d.seq); })
						.attr("font-size", 12).attr("font-family", "Arial")
						.style("opacity", 0);

	overlayText.transition().duration(250).style("opacity", 1);

}


function draw_heatmap(json) {
	var peaks = json.data;

	var row_names = json.y_labels, 
		col_names = json.x_labels,
		structures = json.precalc_structures;

	w = 10, h = 10;
	main_margin = {"left": 0, "top": 0, "right": 0, "bottom": 0};
	var	total_w = col_names.length * (w+0.5),
		total_h = row_names.length * (h+0.5);

	var colorScale = d3.scale.linear()
		.domain([json.peak_min, json.peak_mean + color_scale*json.peak_sd])
		.range(['white', 'black']);
	$("#peak_max").text(json.peak_max.toFixed(2));
	$("#peak_min").text(json.peak_min.toFixed(2));	
	$("#seqA").css("color", get_nt_color("A"));
	$("#seqU").css("color", get_nt_color("U"));
	$("#seqC").css("color", get_nt_color("C"));
	$("#seqG").css("color", get_nt_color("G"));

	var svg = d3.select("#main").append("svg")
			.attr("width", total_w)
			.attr("height", total_h)
			.append("g")

	var temp_lbl = d3.max(row_names, function(d) { return d.length; });
	svg.append("text").text(Array(temp_lbl).join('W'))
		.each(function() { main_margin.right = this.getBBox().width +15; })
		.remove();
	var temp_lbl = d3.max(col_names, function(d) { return d.length; });
	svg.append("text").text(Array(temp_lbl).join('W'))
		.each(function() { main_margin.top = this.getBBox().width +15; })
		.remove();
	svg.append("text").text(Array(col_names.length.toString().length).join('W'))
		.each(function() { main_margin.bottom = this.getBBox().width +15; })
		.remove();
	svg.append("text").text(Array(row_names.length.toString().length).join('W'))
		.each(function() { main_margin.left = this.getBBox().width +15; })
		.remove();
	d3.select("#main").selectAll("svg").remove();

	var svg = d3.select("#main").append("svg")	
				.attr("width", total_w + main_margin.left + main_margin.right)
				.attr("height", total_h + main_margin.top + main_margin.bottom)
				.append("g");

	var y_label_bg = svg.selectAll("g")
					.data(row_names).enter()
					.append("text")
					.text(function(d) { return d; })
					.attr("text-anchor", "start")
					.attr("y", function(d, i) { return (i+.8) * (h+0.5) + main_margin.top;})
					.attr("x", main_margin.left +total_w +5)
					.attr("font-size", 12).attr("font-family", "Arial");
	var y_label = svg.selectAll("g")
					.data(row_names).enter()
					.append("text")
					.text(function(d) { return d; })
					.attr("text-anchor", "start")
					.attr("y", function(d, i) { return (i+.8) * (h+0.5) + main_margin.top;})
					.attr("x", main_margin.left +total_w +5)
					.attr("font-size", 12).attr("font-family", "Arial");
	var x_label_bg = svg.selectAll("g")
					.data(col_names).enter()
					.append("text")
					.text(function(d) { return d.substring(1); })
					.attr("text-anchor", "start")
					.attr("transform", function(d, i) { return "rotate(-90)translate("+ (-main_margin.top +15) + "," + ((i+.8) * (h+0.5) + main_margin.left) + ")"; })
					.attr("font-size", 12).attr("font-family", "Arial");
	var x_label2_bg = svg.selectAll("g")
					.data(col_names).enter()
					.append("text")
					.text(function(d) { return d.substring(0,1); })
					.attr("text-anchor", "start")
					.attr("transform", function(d, i) { return "rotate(-90)translate("+ (-main_margin.top +5) + "," + ((i+.8) * (h+0.5) + main_margin.left) + ")"; })
					.attr("font-size", 12).attr("font-family", "Arial")
					.attr("fill", "white");
	var x_label = svg.selectAll("g")
					.data(col_names).enter()
					.append("text")
					.text(function(d) { return d.substring(1); })
					.attr("text-anchor", "start")
					.attr("transform", function(d, i) { return "rotate(-90)translate("+ (-main_margin.top +15) + "," + ((i+.8) * (h+0.5) + main_margin.left) + ")"; })
					.attr("font-size", 12).attr("font-family", "Arial");
	var x_label2 = svg.selectAll("g")
					.data(col_names).enter()
					.append("text")
					.attr("class", "color")
					.text(function(d) { return d.substring(0,1); })
					.attr("text-anchor", "start")
					.attr("transform", function(d, i) { return "rotate(-90)translate("+ (-main_margin.top +5) + "," + ((i+.8) * (h+0.5) + main_margin.left) + ")"; })
					.attr("font-size", 12).attr("font-family", "Arial")
					.attr("fill", function(d) { return get_nt_color(d.substring(0,1)); });
	var y_num_bg = svg.selectAll("g")
					.data(d3.range(row_names.length)).enter()
					.append("text")
					.text(function(d) { return d+1; })
					.attr("class", "num")
					.attr("text-anchor", "end")
					.attr("y", function(d, i) { return (i+.8) * (h+0.5) + main_margin.top;})
					.attr("x", main_margin.left -5)
					.attr("font-size", 12).attr("font-family", "Arial");
	var y_num = svg.selectAll("g")
					.data(d3.range(row_names.length)).enter()
					.append("text")
					.text(function(d) { return d+1; })
					.attr("class", "num")
					.attr("text-anchor", "end")
					.attr("y", function(d, i) { return (i+.8) * (h+0.5) + main_margin.top;})
					.attr("x", main_margin.left -5)
					.attr("font-size", 12).attr("font-family", "Arial");
	var x_num_bg = svg.selectAll("g")
					.data(d3.range(col_names.length)).enter()
					.append("text")
					.text(function(d) { return d+1; })
					.attr("class", "num")
					.attr("text-anchor", "end")
					.attr("transform", function(d, i) { return "rotate(-90)translate("+ (-main_margin.top -total_h -5) + "," + ((i+.8) * (h+0.5) + main_margin.left) + ")"; })
					.attr("font-size", 12).attr("font-family", "Arial");
	var x_num = svg.selectAll("g")
					.data(d3.range(col_names.length)).enter()
					.append("text")
					.text(function(d) { return d+1; })
					.attr("class", "num")
					.attr("text-anchor", "end")
					.attr("transform", function(d, i) { return "rotate(-90)translate("+ (-main_margin.top -total_h -5) + "," + ((i+.8) * (h+0.5) + main_margin.left) + ")"; })
					.attr("font-size", 12).attr("font-family", "Arial");

	var div = d3.select("body").append("div")
				.attr("class", "tooltip")
				.style("opacity", 0);

    var heatMap = svg.selectAll("g")
					.data(peaks, function(d) { return d.y + ':' + d.x; }).enter()
					.append("svg:rect")
					.attr("class", "tile")
					.attr("y", function(d) { return d.x * (h+0.5) + main_margin.top; })
					.attr("x", function(d) { return d.y * (w+0.5) + main_margin.left; })
					.attr("width", w)
					.attr("height", h)
					.style("fill", function(d) { return colorScale(d.value); })
					.style({"stroke":"black", "stroke-width": 1})
					.on("mouseover", function(d) { 
						var tile = d3.select(this), x_cord = tile.attr("x"), y_cord = tile.attr("y");
						x_cord = (x_cord - main_margin.left)/(w+0.5);
						y_cord = (y_cord - main_margin.top)/(h+0.5);

						heatMap.filter(function(d) { return d.x == y_cord; }).classed("side", true);
						heatMap.filter(function(d) { return d.y == x_cord; }).classed("side", true);

						y_num.filter(function(d, i) { return i == y_cord; }).classed("active", true);
						y_label.filter(function(d, i) { return i == y_cord; }).classed("active", true);
						x_num.filter(function(d, i) { return i == x_cord; }).classed("active", true);
						x_label.filter(function(d, i) { return i == x_cord; }).classed("active", true);
						x_label2.filter(function(d, i) { return i == x_cord; }).classed("side", true);

						y_num_bg.filter(function(d, i) { return i == y_cord; }).classed("highlight", true);
						y_label_bg.filter(function(d, i) { return i == y_cord; }).classed("highlight", true);
						x_num_bg.filter(function(d, i) { return i == x_cord; }).classed("highlight", true);
						x_label_bg.filter(function(d, i) { return i == x_cord; }).classed("highlight", true);
						x_label2_bg.filter(function(d, i) { return i == x_cord; }).classed("highlight", true);

						tile.classed("side", false).classed("active", true);
					})
					.on("mouseout", function(d) { 
						var tile = d3.select(this), x_cord = tile.attr("x"), y_cord = tile.attr("y");
						x_cord = (x_cord - main_margin.left)/(w+0.5);
						y_cord = (y_cord - main_margin.top)/(h+0.5);

						heatMap.filter(function(d) { return d.x == y_cord; }).classed("side", false);
						heatMap.filter(function(d) { return d.y == x_cord; }).classed("side", false);

						y_num.filter(function(d, i) { return i == y_cord; }).classed("active", false);
						y_label.filter(function(d, i) { return i == y_cord; }).classed("active", false);
						x_num.filter(function(d, i) { return i == x_cord; }).classed("active", false);
						x_label.filter(function(d, i) { return i == x_cord; }).classed("active", false);
						x_label2.filter(function(d, i) { return i == x_cord; }).classed("side", false);

						y_num_bg.filter(function(d, i) { return i == y_cord; }).classed("highlight", false);
						y_label_bg.filter(function(d, i) { return i == y_cord; }).classed("highlight", false);
						x_num_bg.filter(function(d, i) { return i == x_cord; }).classed("highlight", false);
						x_label_bg.filter(function(d, i) { return i == x_cord; }).classed("highlight", false);
						x_label2_bg.filter(function(d, i) { return i == x_cord; }).classed("highlight", false);

						tile.classed("active", false);
						div.transition().duration(200)
							.style("opacity", 0)
							.each("end", function() {
								div.style("left", "0px").style("top", "0px");
							});
					})
					.on("click", function(d) {
						var tile = d3.select(this), x_cord = tile.attr("x"), y_cord = tile.attr("y");
						x_cord = (x_cord - main_margin.left)/(w+0.5);
						y_cord = (y_cord - main_margin.top)/(h+0.5);

						div.transition().duration(200)
							.style("opacity", .9);
						div.html("<table><tr><td><p><span class=\"label label-violet pull-right\">ROW</span></p></td><td><p>&nbsp;&nbsp;<span class=\"label label-orange\">" + (y_cord+1) + "</span>: " + row_names[y_cord] + "</p></td></tr><tr><td><p><span class=\"label label-violet pull-right\">COLUMN</span></p></td><td><p>&nbsp;&nbsp;<span class=\"label label-orange\">" + (x_cord+1) + "</span>: " + col_names[x_cord] + "</p></td></tr><tr><td><p><span class=\"label label-primary pull-right\">SEQUENCE</span></p></td><td><p>&nbsp;&nbsp;" + d.seq + "</p></td></tr><tr><td><p><span class=\"label label-success pull-right\">REACTIVITY</span></p></td><td><p>&nbsp;&nbsp;" + d.value + "</p></td></tr><tr><td><p><span class=\"label label-dark-red pull-right\">ERROR</span></p></td><td><p>&nbsp;&nbsp;" + d.error + "</p></td></tr></table>")  
							.style("left", (d3.event.pageX) + "px")
							.style("top", (d3.event.pageY - 28) + "px"); 
					})
					.on("contextmenu", function(d) {
						d3.event.preventDefault();

						var tile = d3.select(this), y_cord = tile.attr("y");
						idx = (y_cord - main_margin.top)/(h+0.5);
						make_barplot(idx);
						$("#page_num").val((idx+1).toString());
						$("#img_panel").addClass("visible").animate({"margin-left":"0px"}).css("z-index", "100");
					});

}