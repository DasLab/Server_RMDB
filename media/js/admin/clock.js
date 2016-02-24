var monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
var weekNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];


function zfill(num, len) {
 return (Array(len).join("0") + num).slice(-len);
}


setInterval(function () {
	var utc = new Date().toISOString().replace(/\..+/, '.000Z');
	$("#utc").html(utc);
    var d = new Date();
    var ampm = (d.getHours() >= 12) ? "p.m." : "a.m.", hour = (d.getHours() >= 12) ? d.getHours() - 12 : d.getHours(); 
    var tz = d.toString().match(/\(([A-Za-z\s].*)\)/)[1].replace(/[a-z ]/g, '');
    $("#date").html(monthNames[d.getMonth()] + ' ' + zfill(d.getDate(), 2) + ', ' + d.getFullYear() + ' (' + weekNames[d.getDay()] + ')');
    $("#clock").html(zfill(hour, 2) + ':' + zfill(d.getMinutes(), 2) + ' ' + ampm + ' (' + tz + ')');
}, 1000);

