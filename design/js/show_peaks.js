var numbers = [1, 1.2, 1.7, 1.5, .7, .2];

var panelWidth = 150;

var barWidth = panelWidth/numbers.length;

var v;
v = new pv.Panel().width(panelWidth).height(140)
.add(pv.Bar)
.data(numbers)
.bottom(0).width(barWidth)
.height(function(d){ return d * 80;})
.left(function(){ return this.index * barWidth;});

v.render();


