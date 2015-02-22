function get_nt_color(nt) {
	switch (nt) {
		case "A":
		case "a":
			return "#ff912e"
		case "T":
		case "t":
		case "U":
		case "u":
			return "#3ed4e7"
		case "C":
		case "c":
			return "#65ff3f"
		case "G":
		case "g":
			return "#ff69bc"
		case "X":
		case "x":
		default:
			return "#a19193"
	}
}

function make_barplot(idx) {
	var margin = {top: 20, right: 140, bottom: 75, left: 75};

	var row_lim = json.row_lim[idx], 
		x_min = 0, x_max = row_lim.x_max -row_lim.x_min +1, 
		y_min = row_lim.y_min, y_max = row_lim.y_max;
	var title = json.y_labels[idx], x_labels = json.x_labels;
	var hdata = json.data.filter(function(d) { return d.x == idx; });

	var barWidth = 10,
		w = barWidth * hdata.length, h = 175, 
		x = d3.scale.linear().domain([ x_min, x_max ]).range([0,w]),
		y = d3.scale.linear().domain([ y_min, y_max ]).range([h,0]);

	d3.select(".chart").selectAll("g, text, line").remove();
	var chart = d3.select(".chart")
				.attr("width", w + margin.left + margin.right)
				.attr("height", h + margin.top + margin.bottom);

	var x_ticks = d3.range( x_min + (5-x_min%5), x_max, 5), y_ticks;
	if (y_max < 5) {
		y_ticks = d3.range( y_min, y_max, 0.5);
	} else {
		if (y_max < 100) {
			var y_intvl = Math.round(y_max / 10);
		} else {
			var y_intvl = Math.round(y_max / 100)*10;
		}
		y_ticks = d3.range( y_min, y_max, y_intvl);
	}
	var colors = d3.scale.linear().domain([0,(y_max - 0.5)/2, y_max - 0.5]).range(["white", "orange", "red"]);

	for (i = 0; i < y_ticks.length; i++) {
		chart.append("line")
			.attr("x1", x(x_min) +margin.left).attr("x2", x(x_max) +margin.left +barWidth/2 +5)
			.attr("y1", y(y_ticks[i]) +margin.top).attr("y2", y(y_ticks[i]) +margin.top)
			.attr("stroke", "#ccc").attr("stroke-width", "1px");
	}
	for (i = 0; i < x_ticks.length; i++) {
		chart.append("line")
			.attr("x1", x(x_ticks[i]) +margin.left +5 +barWidth/2).attr("x2", x(x_ticks[i]) +margin.left +5 +barWidth/2)
			.attr("y1", h +margin.top).attr("y2", margin.top)
			.attr("stroke", "#ccc").attr("stroke-width", "1px");
	}

	var bar = chart.selectAll("g").data(hdata).enter().append("g");
	bar.append("rect")
		.attr("x", function(d) { return x(d.y) -barWidth/2 +5 +margin.left; })
		.attr("y", function(d) { return y(d.value) +margin.top; })
		.attr("height", function(d) { return Math.max(0, h -y(d.value)); })
		.attr("width", barWidth)
		.attr("stroke", "black").attr("stroke-width", "2px")
		.attr("fill", function(d) { return colors(d.value); });
	bar.append("line")
		.attr("x1", function(d) { return x(d.y) + 5 + margin.left; })
		.attr("x2", function(d) { return x(d.y) + 5 + margin.left; })
		.attr("y1", function(d) { 
			if (isNaN(d.error)) { err = 0; } else { err = d.error; }
			return y(d.value-err) +margin.top; 
		})
		.attr("y2", function(d) { 
			if (isNaN(d.error)) { err = 0; } else { err = d.error; }
			return y(d.value+err) +margin.top; 
		})
		.attr("stroke", "black");

	bar.append("line")
		.attr("x1", x(x_min) +margin.left).attr("x2", x(x_max) +margin.left +barWidth/2 +5)
		.attr("y1", h+margin.top).attr("y2", h+margin.top)
		.attr("stroke", "black").attr("stroke-width", "1px");
	bar.append("text")
		.text(function(d,i) { return x_labels[i].substring(0,1); })
		.attr("text-anchor", "end")
		.attr("transform", function(d) { return "rotate(-90)translate(" + -(h +margin.top +8) + "," + (x(d.y) +9 +margin.left) + ")"; })
		.attr("font-size", 12).attr("font-family", "Arial").attr("font-weight", "bold")
		.attr("fill", function(d,i) { return get_nt_color(x_labels[i].substring(0,1)); });
	bar.append("text")
		.text(function(d,i) { return x_labels[i].substring(1); })
		.attr("text-anchor", "end")
		.attr("transform", function(d) { return "rotate(-90)translate(" + -(h +margin.top +18) + "," + (x(d.y) +9 +margin.left) + ")"; })
		.attr("font-size", 12).attr("font-family", "Arial");

	bar.append("line")
		.attr("x1", x( x_min )+margin.left).attr("x2", x( x_min )+margin.left)
		.attr("y1", h+margin.top).attr("y2", margin.top)
		.attr("stroke", "black").attr("stroke-width", "1px");
	bar.append("line")
		.attr("x1", x(x_max) +margin.left +barWidth/2 +5).attr("x2", x(x_max) +margin.left +barWidth/2 +5)
		.attr("y1", h+margin.top).attr("y2", margin.top)
		.attr("stroke", "black").attr("stroke-width", "1px");

	var	yAxis_left = d3.svg.axis().orient("left").scale(y)
					.tickValues(y_ticks),
		yAxis_right = d3.svg.axis().orient("right").scale(y)
					.tickValues(y_ticks);
	chart.append("g")
		.attr("class", "axis")
		.attr("transform", "translate(" + (margin.left +x(x_min)) + "," + margin.top + ")")
		.call(yAxis_left);
	chart.append("g")
		.attr("class", "axis")
		.attr("transform", "translate(" + (margin.left +x(x_max) +barWidth/2 +5) + "," + margin.top + ")")
		.call(yAxis_right);

	chart.append("linearGradient")
		.attr("id", "color_grad")
		.attr("x1", "0%").attr("y1", "100%")
		.attr("x2", "0%").attr("y2", "0%")
		.selectAll("stop")
		.data([
			{offset: "0%", color: "white"},
			{offset: "50%", color: "orange"},
			{offset: "100%", color: "red"}
		])
		.enter().append("stop")
		.attr("offset", function(d) { return d.offset; })
		.attr("stop-color", function(d) { return d.color; });
	bar.append("rect")
		.attr("x", x(x_max) +margin.left +barWidth*5).attr("y", margin.top + h*0.4)
		.attr("height", h*0.5).attr("width", barWidth*2)
		.attr("fill", "url(#color_grad)")
		.attr("stroke", "black").attr("stroke-width", "1px");
	chart.append("text")
		.attr("x", x(x_max) +margin.left +barWidth*5).attr("y", margin.top + h*0.3)
		.text("Legend")
		.attr("font-weight", "bold").attr("font-family", "Arial");
	chart.append("text")
		.attr("x", x(x_max) +margin.left +barWidth*8).attr("y", margin.top + h*0.45)
		.text((y_max-0.5).toFixed(2)).attr("font-family", "Arial");
	chart.append("text")
		.attr("x", x(x_max) +margin.left +barWidth*8).attr("y", margin.top + h*0.9)
		.text(y_min.toFixed(2)).attr("font-family", "Arial");

	chart.append("text")
		.text("Normalized Reactivity")
		.attr("text-anchor", "end")
		.attr("transform", "rotate(-90)translate(-30,35)")
		.attr("font-size", 15).attr("font-weight", "bold").attr("font-family", "Arial");
	chart.append("text")
		.text("Sequence Position")
		.attr("transform", "translate("+ (w/2+25) +","+ (margin.top+h+60) +")")
		.attr("font-size", 15).attr("font-weight", "bold").attr("font-family", "Arial");
	chart.append("text")
		.text("Barplot for row_#" + (idx+1).toString() + ": " + title)
		.attr("transform", "translate("+ (w/2-10) +","+ (margin.top-5) +")")
		.attr("font-size", 18).attr("font-weight", "bold").attr("font-family", "Arial");
	chart.attr("num", (idx+1).toString());
	chart.attr("ttl", title);
}


$(document).ready(function() {

	$("#svg_top").on("click", function() {
		idx = 0;
		make_barplot(idx);
		$("#page_num").val((idx+1).toString());
	});
	$("#svg_bottom").on("click", function() {
		idx = n_rows-1;
		console.log(idx);
		make_barplot(idx);
		$("#page_num").val((idx+1).toString());
	});
	$("#svg_up").on("click", function() {
		if (idx > 0) {
			idx -= 1;
			make_barplot(idx);
		}
		$("#page_num").val((idx+1).toString());
	});
	$("#svg_down").on("click", function() {
		if (idx < n_rows-1) {
			idx += 1;
			make_barplot(idx);
		}
		$("#page_num").val((idx+1).toString());
	});
	$("#svg_save").on("click", function () {
		var svg_dom = d3.select(".chart")
					.attr("version", 1.1)
					.attr("xmlns", "http://www.w3.org/2000/svg")
					.node().parentNode;

		var s = document.createElement("style");
		s.setAttribute('type', 'text/css');
		var svg_file = ""
		$.get("/site_media/css/svg_barplot.css", function(txt) { 
			s.innerHTML = "<![CDATA[\n" + txt + "\n]]>"
			var defs = document.createElement('defs');
			defs.appendChild(s);
			svg_dom.firstChild.insertBefore(defs, svg_dom.firstChild.firstChild);
			var svg_html = svg_dom.innerHTML;
			svg_file = "data:image/svg+xml;base64," + btoa(svg_html);
		}).done(function() {
			var svg_name = "barplot_row" + $(".chart").attr("num") + "_" 
							+ $(".chart").attr("ttl").replace(",","-").replace("/","-").replace("\\","-").replace(";","-").replace(":","-") 
							+ ".svg"
			var tmp = document.createElement("a");
			tmp.setAttribute("download", svg_name);
			tmp.setAttribute("href", svg_file);
			tmp.setAttribute("target", "_blank");
			tmp.click();
		});
		return false;
	});
	$("#svg_setting").on("click", function () {
		if ($("#set_panel").hasClass("visible")) {
			$("#set_panel").animate({"margin-right":"-"+$("#set_panel").css("width")}).removeClass("visible").css("z-index", "1");
		} else {
			$("#set_panel").animate({"margin-right":"0px"}).addClass("visible").css("z-index", "200");
		}
	});
	$("#svg_clear").on("click", function () {
		d3.select(".chart").selectAll("g, text, line").remove();
		$("#page_num").val("");
	});
	$("#page_num").on("focusout", function () {
		var idx_tmp = parseInt($(this).val());
		if (!isNaN(idx_tmp)){
			if (idx_tmp < 0) {idx_tmp = 0;}
			if (idx_tmp > n_rows-1) {idx_tmp = n_rows-1;}
			idx = idx_tmp-1;
			make_barplot(idx);
			$("#page_num").val((idx+1).toString());
		}
	});
	$("#page_num").on("keyup", function (e) {
		if(e.keyCode == 13) {$(this).trigger("focusout");}
	});
});