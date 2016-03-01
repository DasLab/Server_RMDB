sudo rm media/js/admin/min/*.min.js
java -jar ../yuicompressor.jar -o '.js$:.min.js' media/js/admin/*.js
mv media/js/admin/*.min.js media/js/admin/min/

sudo rm media/js/public/min/*.min.js
java -jar ../yuicompressor.jar -o '.js$:.min.js' media/js/public/*.js
mv media/js/public/*.min.js media/js/public/min/

sudo rm media/js/suit/min/*.min.js
java -jar ../yuicompressor.jar -o '.js$:.min.js' media/js/suit/*.js
mv media/js/suit/*.min.js media/js/suit/min/

sudo rm media/css/min/*.min.css
java -jar ../yuicompressor.jar -o '.css$:.min.css' media/css/*.css
rm media/css/*.min.min.css
mv media/css/*.min.css media/css/min/
mv media/css/min/bootstrap.min.css media/css/

cat media/js/public/min/view_util.min.js media/js/public/min/view_tags.min.js media/js/public/min/view_heatmap.min.js media/js/public/min/view_barplot.min.js media/js/public/min/view_setting.min.js media/js/public/min/view.min.js > media/js/public/min/view.js
rm media/js/public/min/view*.min.js
mv media/js/public/min/view.js media/js/public/min/view.min.js
