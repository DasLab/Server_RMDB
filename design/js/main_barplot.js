$(document).ready(function() {

	$("#svg_top").on("click", function() {
		idx = 0;
		make_barplot(idx);
		$("#page_num").val((idx+1).toString());
	});
	$("#svg_bottom").on("click", function() {
		idx = rows.length-1;
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
		if (idx < rows.length-1) {
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
		$.get("/site_media/css/svg.css", function(txt) { 
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
			if (idx_tmp > rows.length-1) {idx_tmp = rows.length-1;}
			idx = idx_tmp-1;
			make_barplot(idx);
			$("#page_num").val((idx+1).toString());
		}
	});
	$("#page_num").on("keyup", function (e) {
		if(e.keyCode == 13) {$(this).trigger("focusout");}
	});
});