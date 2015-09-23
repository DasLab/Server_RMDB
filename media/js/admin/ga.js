(function(w,d,s,g,js,fs){
    g=w.gapi||(w.gapi={});g.analytics={q:[],ready:function(f){this.q.push(f);}};
    js=d.createElement(s);fs=d.getElementsByTagName(s)[0];
    js.src='https://apis.google.com/js/platform.js';
    fs.parentNode.insertBefore(js,fs);js.onload=function(){g.load('analytics');};
}(window,document,'script'));

var gviz_handles = [], resize_flag = false;

function readyHandler() {
    $(".place_holder").each(function() {
        if ($(this).html().length > 0) { $(this).removeClass("place_holder"); }
    });
}


function drawGA(id) {
    new gapi.analytics.ViewSelector({ 'container': 'view-selector-container' }).execute();

    var chart = new gapi.analytics.googleCharts.DataChart({
        'query': {
            'ids': id,
            'metrics': 'ga:sessions',
            'dimensions': 'ga:dateHour',
            'start-date': 'yesterday',
            'end-date': 'today'
        },
        'chart': {
            'container': 'chart_24h',
            'type': 'LINE',
            'options': {
                'width': '100%',
                'height': '25%',
                'title': 'Last 24 Hours',
                'colors': ['#c28fdd'],
                'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
            }
        }
    });
    chart.once('success', readyHandler).execute();
    gviz_handles.push(chart);
    var chart = new gapi.analytics.googleCharts.DataChart({
        'query': {
            'ids': id,
            'metrics': 'ga:sessions',
            'dimensions': 'ga:date',
            'start-date': '7daysAgo',
            'end-date': 'today'
        },
        'chart': {
            'container': 'chart_7d',
            'type': 'LINE',
            'options': {
                'width': '100%',
                'height': '25%',
                'title': 'Last 7 Days',
                'colors': ['#d86f5c'],
                'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
            }
        }
    });
    chart.once('success', readyHandler).execute();
    gviz_handles.push(chart);
    var chart = new gapi.analytics.googleCharts.DataChart({
        'query': {
            'ids': id,
            'metrics': 'ga:sessions',
            'dimensions': 'ga:date',
            'start-date': '30daysAgo',
            'end-date': 'yesterday'
        },
        'chart': {
            'container': 'chart_1m',
            'type': 'LINE',
            'options': {
                'width': '100%',
                'height': '25%',
                'title': 'Last 30 Days',
                'colors': ['#ff912e'],
                'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
            }
        }
    });
    chart.once('success', readyHandler).execute();
    gviz_handles.push(chart);
    var chart = new gapi.analytics.googleCharts.DataChart({
        'query': {
            'ids': id,
            'metrics': 'ga:sessions',
            'dimensions': 'ga:date',
            'start-date': '90daysAgo',
            'end-date': 'yesterday'
        },
        'chart': {
            'container': 'chart_3m',
            'type': 'LINE',
            'options': {
                'width': '100%',
                'height': '25%',
                'title': 'Last 90 Days',
                'colors': ['#29be92'],
                'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
            }
        }
    });
    chart.once('success', readyHandler).execute();
    gviz_handles.push(chart);

    var chart = new gapi.analytics.googleCharts.DataChart({
        'query': {
            'ids': id,
            'metrics': 'ga:sessions',
            'dimensions': 'ga:country',
            'start-date': '30daysAgo',
            'end-date': 'yesterday'
        },
        'chart': {
            'container': 'geo_session',
            'type': 'GEO',
            'options': {
                'width': '100%',
                'title': 'Sessions',
                'colorAxis': {'colors': ['#ddf6f0','#5496d7']},
                'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
            }
        }
    });
    chart.once('success', readyHandler).execute();
    gviz_handles.push(chart);

    var chart = new gapi.analytics.googleCharts.DataChart({
        'query': {
            'ids': id,
            'metrics': 'ga:sessions',
            'dimensions': 'ga:userType',
            'start-date': '30daysAgo',
            'end-date': 'yesterday'
        },
        'chart': {
            'container': 'pie_session',
            'type': 'PIE',
            'options': {
                'width': '100%',
                'title': 'Sessions',
                'legend': {'position': 'bottom'},
                'colors': ['#50cc32', '#ff69bc'],
                'pieHole': 0.33,
                'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
            }
        }
    });
    chart.once('success', readyHandler).execute();
    gviz_handles.push(chart);
    var chart = new gapi.analytics.googleCharts.DataChart({
        'query': {
            'ids': id,
            'metrics': 'ga:users',
            'dimensions': 'ga:userType',
            'start-date': '30daysAgo',
            'end-date': 'yesterday'
        },
        'chart': {
            'container': 'pie_user',
            'type': 'PIE',
            'options': {
                'width': '100%',
                'title': 'Visitors',
                'legend': {'position': 'bottom'},
                'colors': ['#3ed4e7', '#ff912e'],
                'pieHole': 0.33,
                'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
            }
        }
    });
    chart.once('success', readyHandler).execute();
    gviz_handles.push(chart);
    var chart = new gapi.analytics.googleCharts.DataChart({
        'query': {
            'ids': id,
            'metrics': 'ga:users',
            'dimensions': 'ga:browser',
            'start-date': '30daysAgo',
            'end-date': 'yesterday',
            'filters': 'ga:browser=@Firefox,ga:browser=@Chrome,ga:browser=@Safari,ga:browser=@Internet Explorer',
            'sort': 'ga:browser',
            'max-results': 4,
        },
        'chart': {
            'container': 'pie_browser',
            'type': 'PIE',
            'options': {
                'width': '100%',
                'title': 'Browser',
                'legend': {'position': 'bottom', 'maxLines': 2},
                'colors': ['#29be92', '#ff912e', '#5496d7', '#ff5c2b'],
                'pieHole': 0.33,
                'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
            }
        }
    });
    chart.once('success', readyHandler).execute();
    gviz_handles.push(chart);
    var chart = new gapi.analytics.googleCharts.DataChart({
        'query': {
            'ids': id,
            'metrics': 'ga:pageviews',
            'dimensions': 'ga:userType',
            'start-date': '30daysAgo',
            'end-date': 'yesterday',
        },
        'chart': {
            'container': 'pie_pageview',
            'type': 'PIE',
            'options': {
                'width': '100%',
                'title': 'Page Views',
                'legend': {'position': 'bottom'},
                'colors': ['#8ee4cf', '#c28fdd'],
                'pieHole': 0.33,
                'animation': {'startup': true, 'duration': 1000, 'easing': 'inAndOut'}
            }
        }
    });
    chart.once('success', readyHandler).execute();
    gviz_handles.push(chart);
}


gapi.analytics.ready(function() {
    $.ajax({
        url : "/admin/ga_admin",
        dataType: "json",
        success: function (data) {
            gapi.analytics.auth.authorize({
                'container': 'embed-api-auth-container',
                'clientid': data.client_id,
                'serverAuth': { 'access_token': data.access_token }
            });
            new gapi.analytics.ViewSelector({ 'container': 'view-selector-container' }).execute();

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

            drawGA('ga:' + data.id);
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
});



$(window).on("resize", function() {
    clearTimeout($(window).data(this, 'resizeTimer'));
    $(window).data(this, 'resizeTimer', setTimeout(function() {
        if (!resize_flag) {
            resize_flag = true
            for (var i = 0; i < gviz_handles.length; i++) {
                gviz_handles[i].execute();
            }
            setTimeout(function() { resize_flag = false; }, 1000);
        }
    }, 200));
});




