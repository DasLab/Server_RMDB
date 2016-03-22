google.load('visualization', '1', {packages: ['corechart', 'calendar']});
google.setOnLoadCallback(drawDash);
var gviz_handles = [];

function readyHandler() {
    $(".place_holder").each(function() {
        if ($(this).html().length > 0) { $(this).removeClass("place_holder"); }
    });
}


function drawDash() {
    var chart = new google.visualization.ChartWrapper({
        'chartType': 'Calendar',
        'dataSourceUrl': '/admin/git_stat/?qs=c',
        'containerId': 'plot_c',
        'options': {
            'title': 'Last Year',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'calendar': {
                'cellColor': {'stroke': '#fff'},
                'underYearSpace': 20,
                'yearLabel': {'color': '#c28fdd', 'bold': true},
                'monthLabel': {'color': '#000'},
                'monthOutlineColor': {'stroke': '#d86f5c', 'strokeOpacity': 0.8, 'strokeWidth': 2},
                'dayOfWeekLabel': {'color': '#000'}
            },
            'colorAxis': {
                'values': [0, 3, 6, 9, 12],
                'colors': ['#f8f8f8', '#fae621', '#5cc861', '#23888d', '#3a518a']
            },
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);

    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/git_stat/?qs=ad',
        'containerId': 'plot_ad',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Weekly Aggregation',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
                'scaleType': 'mirrorLog',
                'format': 'scientific',
                'gridlines': {'count': 5}
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM yy'
            },
            'tooltip': {'showColorCode': true},
            'focusTarget': 'category',
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#29be92', '#ff5c2b'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);

    chart = new google.visualization.ChartWrapper({
        'chartType': 'PieChart',
        'dataSourceUrl': '/admin/git_stat/?qs=au',
        'containerId': 'plot_pie',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Contributors Commits',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'pieHole': 0.33,
            'colors': ['#3ed4e7', '#ff912e', '#29be92', '#ff5c2b'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);

}


$.ajax({
    url : "/admin/git_stat/?qs=init&tqx=reqId%3A52",
    dataType: "json",
    success: function (data) {
        var html = "";
        for (var i = 0; i < data.contrib.length; i++) {
            html += '<tr><td>' + data.contrib[i].Contributors + '</td><td><span class="pull-right" style="color:#00f;">' + data.contrib[i].Commits + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></td><td><span class="pull-right" style="color:#080;">' + data.contrib[i].Additions + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></td><td><span class="pull-right" style="color:#f00;">' + data.contrib[i].Deletions + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></td></tr>';
        }
        html += '<tr><td colspan="4" style="padding: 0px;"></td></tr>';
        $("#git_table_body").html(html).removeClass('place_holder');
    }
});

$.ajax({
    url : "/admin/git_stat/?qs=num&tqx=reqId%3A53",
    dataType: "json",
    success: function (data) {
        $("#git_num_body").html('<tr><td><span class="label label-green">created</span></td><td><span class="label label-primary">' + data.created_at + '</span></td></tr><tr><td><span class="label label-dark-green">last pushed</span></td><td><span class="label label-primary">' + data.pushed_at + '</span></td></tr><tr><td><span class="label label-danger">issue</span></td><td>' + data.num_issues + '</td></tr><tr><td><span class="label label-info">download</span></td><td>' + data.num_downloads + '</td></tr><tr><td><span class="label label-info">pull</span></td><td>' + data.num_pulls + '</td></tr><tr><td><span class="label label-orange">branch</span></td><td>' + data.num_branches + '</td></tr><tr><td><span class="label label-orange">fork</span></td><td>' + data.num_forks + '</td></tr><tr><td><span class="label label-violet">watcher</span></td><td>' + data.num_watchers + '</td></tr><tr><td colspan="2" style="padding: 0px;"></td></tr>').removeClass('place_holder');
    }
});


$(window).on("resize", function() {
    clearTimeout($(window).data(this, 'resizeTimer'));
    $(window).data(this, 'resizeTimer', setTimeout(function() {
        for (var i = 0; i < gviz_handles.length; i++) {
            gviz_handles[i].draw();
        }
    }, 200));
});


