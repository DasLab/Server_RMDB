function draw_heatmap(json) {
	var peaks = json.data;

	var row_names = json.y_labels, 
		col_names = json.x_labels,
		structures = json.precalc_structures;

	var w = 10, h = 10,
		total_w = col_names.length * w,
		total_h = row_names.length * h
		main_margin = {"left": 0, "top": 0, "right": 0, "bottom": 0};

	var colorScale = d3.scale.linear()
		.domain([json.peak_min, json.peak_max])
		.range(['white', 'black']);
	$("#peak_max").text(json.peak_max.toFixed(2));
	$("#peak_min").text(json.peak_min.toFixed(2));	

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

	var y_label = svg.selectAll("g")
					.data(row_names)
					.enter().append("text")
					.text(function(d) { return d; })
					.attr("text-anchor", "start")
					.attr("y", function(d, i) { return (i+.8) * h + main_margin.top;})
					.attr("x", main_margin.left +total_w +5)
					.attr("font-size", 12).attr("font-family", "Arial");
	var x_label = svg.selectAll("g")
					.data(col_names)
					.enter().append("text")
					.text(function(d) { return d; })
					.attr("text-anchor", "start")
					.attr("transform", function(d, i) { return "rotate(-90)translate("+ (-main_margin.top +5) + "," + ((i+.8) * h + main_margin.left) + ")"; })
					.attr("font-size", 12).attr("font-family", "Arial");
	var y_num = svg.selectAll("g")
					.data(d3.range(row_names.length))
					.enter().append("text")
					.text(function(d) { return d+1; })
					.attr("text-anchor", "end")
					.attr("y", function(d, i) { return (i+.8) * h + main_margin.top;})
					.attr("x", main_margin.left -5)
					.attr("font-size", 12).attr("font-family", "Arial");
	var x_num = svg.selectAll("g")
					.data(d3.range(col_names.length))
					.enter().append("text")
					.text(function(d) { return d+1; })
					.attr("text-anchor", "end")
					.attr("transform", function(d, i) { return "rotate(-90)translate("+ (-main_margin.top -total_h -5) + "," + ((i+.8) * h + main_margin.left) + ")"; })
					.attr("font-size", 12).attr("font-family", "Arial");

	var heatMap = svg.selectAll("g")
					.data(peaks, function(d) { return d.y + ':' + d.x; })
					.enter().append("svg:rect")
					.attr("class", "tile")
					.attr("y", function(d) { return d.x * h + main_margin.top; })
					.attr("x", function(d) { return d.y * w + main_margin.left; })
					.attr("width", w)
					.attr("height", h)
					.style("fill", function(d) { return colorScale(d.value*5); })
					.style({"stroke":"black", "stroke-width": 1});	
}