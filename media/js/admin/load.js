var xmlhttp = new XMLHttpRequest(), isCDN = false;
var ver_jquery, ver_bootstrap, ver_d3;
xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == XMLHttpRequest.DONE) {
        if (xmlhttp.status == 200) {
            var xmlDoc = JSON.parse(xmlhttp.responseText);
            ver_jquery = xmlDoc.jquery;
            ver_bootstrap = xmlDoc.bootstrap;
            ver_d3 = xmlDoc.d3;

            document.write('<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/' + ver_jquery + '/jquery.min.js"><\/script>');
            document.write('\
                <script type="text/javascript"> \
                    if (!window.jQuery) { \
                        document.write(\'<script type="text/javascript" src="/site_media/js/jquery.min.js"><\' + \'/script>\'); \
                        document.write(\'<script type="text/javascript" src="/site_media/js/bootstrap.min.js"><\' + \'/script>\'); \
                        document.write(\'<link rel="stylesheet" href="/site_media/css/bootstrap.min.css" \/>\'); \
                        isCDN = false; \
                    } else { \
                        document.write(\'<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/' + ver_bootstrap + '/js/bootstrap.min.js"><\' + \'/script>\'); \
                        document.write(\'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/' + ver_bootstrap + '/css/bootstrap.min.css" \/>\'); \
                        isCDN = true; \
                    } \
                \x3C\/script>');
        } else {
            document.write('<script type="text/javascript" src="/site_media/js/jquery.min.js"><\/script>');
            document.write('<script type="text/javascript" src="/site_media/js/bootstrap.min.js"><\/script>');
            document.write('<link rel="stylesheet" href="/site_media/css/bootstrap.min.css" \/>');
        }

        if (DEBUG_DIR) {
            document.write('<link rel="stylesheet" href="/site_media/css/' + DEBUG_DIR + 'theme' + DEBUG_STR + '.css" \/>');
        } else {
            document.write('<link rel="stylesheet" href="/site_media/css/theme.css" \/>');
            document.write('<link rel="stylesheet" href="/site_media/css/palette.css" \/>');
        }
        document.write('<link rel="shortcut icon" href="/site_media/images/icon_rmdb.png" \/>');
        document.write('<link rel="icon" type-"image/gif" href="/site_media/images/icon_rmdb.png" \/>');
    }
};
xmlhttp.open("GET", "/get_js/", false);
xmlhttp.send();
