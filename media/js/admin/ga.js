google.load('visualization', '1', {packages: ['corechart']});
google.setOnLoadCallback(drawDash);
var gviz_handles = [];


function readyHandler() {
    $(".place_holder").each(function() {
        if ($(this).html().length > 0) { $(this).removeClass("place_holder"); }
    });
}


function drawDash() {
    $.ajax({
        url : "/admin/ga_stat/?qs=init&tqx=reqId%3A52",
        dataType: "json",
        success: function (data) {
            $("#br").html(data.bounceRate + ' %').removeClass('place_holder');
            $("#br_prv").html(data.bounceRate_prev + ' %');
            $("#u").html(data.users).removeClass('place_holder');
            $("#u_prv").html(data.users_prev);
            $("#sd").html(data.sessionDuration).removeClass('place_holder');
            $("#sd_prv").html(data.sessionDuration_prev);
            $("#s").html(data.sessions).removeClass('place_holder');
            $("#s_prv").html(data.sessions_prev);
            $("#pvs").html(data.pageviewsPerSession).removeClass('place_holder');
            $("#pvs_prv").html(data.pageviewsPerSession_prev);
            $("#pv").html(data.pageviews).removeClass('place_holder');
            $("#pv_prv").html(data.pageviews_prev);
        },
        complete: function () {
            var green = "#50cc32", red = "#ff5c2b";
            if ($("#br_prv").html().indexOf('-') != -1) {
                $("#br_prv_ico").html('<sup><span class="label label-green"><span class="glyphicon glyphicon-arrow-down"></span></span></sup>');
                $("#br_prv").css("color", green);
            } else {
                $("#br_prv_ico").html('<sup><span class="label label-danger"><span class="glyphicon glyphicon-arrow-up"></span></span></sup>');
                $("#br_prv").css("color", red);
                $("#br_prv").html('+' + $("#br_prv").html());
            }
            if ($("#u_prv").html().indexOf('-') != -1) {
                $("#u_prv_ico").html('<sup><span class="label label-green"><span class="glyphicon glyphicon-arrow-down"></span></span></sup>');
                $("#u_prv").css("color", green);
            } else {
                $("#u_prv_ico").html('<sup><span class="label label-danger"><span class="glyphicon glyphicon-arrow-up"></span></span></sup>');
                $("#u_prv").css("color", red);
                $("#u_prv").html('+' + $("#u_prv").html());
            }
            if ($("#sd_prv").html().indexOf('-') != -1) {
                $("#sd_prv_ico").html('<sup><span class="label label-green"><span class="glyphicon glyphicon-arrow-down"></span></span></sup>');
                $("#sd_prv").css("color", green);
            } else {
                $("#sd_prv_ico").html('<sup><span class="label label-danger"><span class="glyphicon glyphicon-arrow-up"></span></span></sup>');
                $("#sd_prv").css("color", red);
                $("#sd_prv").html('+' + $("#sd_prv").html());
            }
            if ($("#s_prv").html().indexOf('-') != -1) {
                $("#s_prv_ico").html('<sup><span class="label label-green"><span class="glyphicon glyphicon-arrow-down"></span></span></sup>');
                $("#s_prv").css("color", green);
            } else {
                $("#s_prv_ico").html('<sup><span class="label label-danger"><span class="glyphicon glyphicon-arrow-up"></span></span></sup>');
                $("#s_prv").css("color", red);
                $("#s_prv").html('+' + $("#s_prv").html());
            }
            if ($("#pvs_prv").html().indexOf('-') != -1) {
                $("#pvs_prv_ico").html('<sup><span class="label label-green"><span class="glyphicon glyphicon-arrow-down"></span></span></sup>');
                $("#pvs_prv").css("color", green);
            } else {
                $("#pvs_prv_ico").html('<sup><span class="label label-danger"><span class="glyphicon glyphicon-arrow-up"></span></span></sup>');
                $("#pvs_prv").css("color", red);
                $("#pvs_prv").html('+' + $("#pvs_prv").html());
            }
            if ($("#pv_prv").html().indexOf('-') != -1) {
                $("#pv_prv_ico").html('<sup><span class="label label-green"><span class="glyphicon glyphicon-arrow-down"></span></span></sup>');
                $("#pv_prv").css("color", green);
            } else {
                $("#pv_prv_ico").html('<sup><span class="label label-danger"><span class="glyphicon glyphicon-arrow-up"></span></span></sup>');
                $("#pv_prv").css("color", red);
                $("#pv_prv").html('+' + $("#pv_prv").html());
            }
        }
    });

    var chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/ga_stat/?qs=chart&sp=24h',
        'containerId': 'chart_24h',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'none'},
            'title': 'Last 24 Hours',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true}
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#c28fdd'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/ga_stat/?qs=chart&sp=7d',
        'containerId': 'chart_7d',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'none'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true}
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#d86f5c'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/ga_stat/?qs=chart&sp=1m',
        'containerId': 'chart_1m',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'none'},
            'title': 'Last 30 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true}
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#ff912e'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/ga_stat/?qs=chart&sp=3m',
        'containerId': 'chart_3m',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'none'},
            'title': 'Last 90 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true}
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#29be92'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);

    chart = new google.visualization.ChartWrapper({
        'chartType': 'PieChart',
        'dataSourceUrl': '/admin/ga_stat/?qs=pie&sp=session',
        'containerId': 'pie_session',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Sessions',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'pieHole': 0.33,
            'colors': ['#50cc32', '#ff69bc'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'PieChart',
        'dataSourceUrl': '/admin/ga_stat/?qs=pie&sp=user',
        'containerId': 'pie_user',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Visitors',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'pieHole': 0.33,
            'colors': ['#3ed4e7', '#ff912e'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'PieChart',
        'dataSourceUrl': '/admin/ga_stat/?qs=pie&sp=browser',
        'containerId': 'pie_browser',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Browser',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'pieHole': 0.33,
            'colors': ['#29be92', '#ff912e', '#5496d7', '#ff5c2b'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'PieChart',
        'dataSourceUrl': '/admin/ga_stat/?qs=pie&sp=pageview',
        'containerId': 'pie_pageview',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Page Views',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'pieHole': 0.33,
            'colors': ['#8ee4cf', '#c28fdd'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);

    chart = new google.visualization.ChartWrapper({
        'chartType': 'GeoChart',
        'dataSourceUrl': '/admin/ga_stat/?qs=geo',
        'containerId': 'geo_session',
        'options': {
            'height': 300,
            'displayMode': 'regions',
            'legend': {'position': 'bottom'},
            'title': 'Sessions',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'colors': ['#ddf6f0','#5496d7'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
}


$(window).on("resize", function() {
    clearTimeout($(window).data(this, 'resizeTimer'));
    $(window).data(this, 'resizeTimer', setTimeout(function() {
        for (var i = 0; i < gviz_handles.length; i++) {
            gviz_handles[i].draw();
        }
    }, 200));
});




