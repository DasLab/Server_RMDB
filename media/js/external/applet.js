    $(document).ready(function(){
    browser = navigator.appName;
    if(browser.indexOf("Explorer") != -1){
        $("#browser_warning").show();
            $(".svg_disabled").show();
            $(".svg_enabled").hide();
        }
    function preventDefault(e) {
      e = e || window.event;
      if (e.preventDefault)
          e.preventDefault();
      e.returnValue = false;  
    }
    function wheel(e) {
      preventDefault(e);
    }
    function disable_scroll() {
      if (window.addEventListener) {
          window.addEventListener("DOMMouseScroll", wheel, false);
      }
      window.onmousewheel = document.onmousewheel = wheel;
    }

    function enable_scroll() {
        if (window.removeEventListener) {
        window.removeEventListener("DOMMouseScroll", wheel, false);
        }
        window.onmousewheel = document.onmousewheel = null;  
    }
        var wheelDistance = function(evt){
        if (!evt) evt = event;
        var w=evt.wheelDelta, d=evt.detail;
        if (d){
            if (w) return w/d/40*d>0?1:-1; // Opera
            else return -d/3;              // Firefox;         TODO: do not /3 for OS X
        } else return w/120;             // IE/Safari/Chrome TODO: /3 for Chrome OS X
    };
    var wheelDirection = function(evt){
        if (!evt) evt = event;
        return (evt.detail<0) ? 1 : (evt.wheelDelta>0) ? 1 : -1;
    };
    $(".appletdiv").bind("mousewheel", function(evt, delta){
        var distance  = wheelDistance(evt);
        var direction = wheelDirection(evt);
        console.log("event.wheelDelta: "+evt.wheelDelta+"<br>event.detail: "+evt.detail+"<br>Normalized Wheel Distance: "+distance+"<br>Wheel Direction: "+direction);
    });
    $(".appletdiv").mouseover(function() {
            disable_scroll();
    });
    $(".appletdiv").mouseout(function() {
            enable_scroll();
    });
    $("#submitform").click(function() {
            $("#advanced_search_form").submit();
            return false;
    });
    $("#submitform").button();

    });
