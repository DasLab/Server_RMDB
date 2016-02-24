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
        url : "/admin/aws_stat/?qs=init&sp=init&tqx=reqId%3A52",
        dataType: "json",
        success: function (data) {
            $("#aws_table_body").parent().remove();

            $("#table_ec2_id").html(data.ec2.id);
            $("#table_ec2_type").html(data.ec2.instance_type);
            $("#table_ec2_img").html(data.ec2.image_id);
            $("#table_ec2_arch").html(data.ec2.architecture);
            $("#table_ec2_vpc").html(data.ec2.vpc_id);
            $("#table_ec2_subnet").html(data.ec2.subnet_id);
            $("#table_ebs_type").html(data.ebs.type);
            $("#table_ebs_id").html(data.ebs.id);
            $("#table_ebs_size").html(data.ebs.size);
            $("#table_ebs_snap").html(data.ebs.snapshot_id);
            $("#table_ebs_zone").html(data.ebs.zone);
            $("#table_elb_vpc").html(data.elb.vpc_id);
            $("#table_elb_health").html(data.elb.health_check);

            $("#table_elb_pns").html(data.elb.dns_name);
            $("#table_elb_pns").parent().css("href", "http://" + data.elb.dns_name);
            $("#table_ec2_pub_dns").html(data.ec2.public_dns_name);
            $("#table_ec2_pub_dns").parent().css("href", "http://" + data.ec2.public_dns_name);
            $("#table_ec2_prv_dns").html(data.ec2.private_dns_name);
            $("#table_ec2_prv_dns").parent().css("href", "http://" + data.ec2.private_dns_name);
        }
    });


    var chart = new google.visualization.ChartWrapper({
        'chartType': 'ColumnChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=latency&sp=48h',
        'containerId': 'plot_lat1',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'none'},
            'title': 'Last 48 Hours',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Milliseconds (ms)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true}
            },
            'bar': {'groupWidth': '500%' },
            'colors': ['#8ee4cf'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=latency&sp=7d',
        'containerId': 'plot_lat2',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'none'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Milliseconds (ms)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM dd'
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#8ee4cf'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);

    chart = new google.visualization.ChartWrapper({
        'chartType': 'ColumnChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=request&sp=48h',
        'containerId': 'plot_req1',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'none'},
            'title': 'Last 48 Hours',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true}
            },
            'bar': {'groupWidth': '500%' },
            'colors': ['#5496d7'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=request&sp=7d',
        'containerId': 'plot_req2',
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
                'textStyle': {'italic': true},
                'format': 'MMM dd'
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#5496d7'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);

    chart = new google.visualization.ChartWrapper({
        'chartType': 'ColumnChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=cpu&sp=48h',
        'containerId': 'plot_cpu1',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'none'},
            'title': 'Last 48 Hours',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Percent (%)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true}
            },
            'bar': {'groupWidth': '500%' },
            'colors': ['#c28fdd'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=cpu&sp=7d',
        'containerId': 'plot_cpu2',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'none'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Percent (%)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM dd'
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
        'dataSourceUrl': '/admin/aws_stat/?qs=host&sp=7d',
        'containerId': 'plot_host',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
                'viewWindow': {'max': 2, 'min': 0},
                'ticks': [0, 1, 2]
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM dd'
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#50cc32', '#ff69bc'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=credit&sp=7d',
        'containerId': 'plot_credit',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
                'viewWindow': {'min': 0},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM dd'
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#ff5c2b', '#29be92'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=status&sp=7d',
        'containerId': 'plot_status',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
                'viewWindow': {'min': 0}
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM dd'
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#ff5c2b', '#ff69bc', '#ff912e'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);

    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=network&sp=7d',
        'containerId': 'plot_net',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Kilobytes/Second (kb/s)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM dd'
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#ff912e', '#3ed4e7'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=volbytes&sp=7d',
        'containerId': 'plot_vol',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Kilobytes/Second (kb/s)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM dd'
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#ff912e', '#3ed4e7'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);

    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=23xx&sp=7d',
        'containerId': 'plot_23xx',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM dd'
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#5496d7', '#29be92'],
            'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
        }
    });
    google.visualization.events.addListener(chart, 'ready', readyHandler);
    chart.draw();
    gviz_handles.push(chart);
    chart = new google.visualization.ChartWrapper({
        'chartType': 'AreaChart',
        'dataSourceUrl': '/admin/aws_stat/?qs=45xx&sp=7d',
        'containerId': 'plot_45xx',
        'options': {
            'chartArea': {'width': '90%', 'left': '10%'},
            'legend': {'position': 'bottom'},
            'title': 'Last 7 Days',
            'titleTextStyle': {'bold': false, 'fontSize': 16},
            'vAxis': {
                'title': 'Count (#)',
                'titleTextStyle': {'bold': true},
            },
            'hAxis': {
                'gridlines': {'count': -1},
                'textStyle': {'italic': true},
                'format': 'MMM dd'
            },
            'lineWidth': 3,
            'pointSize': 5,
            'colors': ['#c28fdd', '#ff5c2b'],
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


