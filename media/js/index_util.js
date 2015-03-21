function convertToSlug(Text) {
  return Text.toLowerCase().replace('/', '')
	.replace(/[^a-z0-9-]/g, '-').replace(/\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

function colorRmdbId(string) {
  string = string.split('_');
  s1 = '<span style="color: yellow;">' + string[1] + '</span>';
  s2 = '<span style="color: skyblue;">' + string[2] + '</span>'; 
  return string[0] + '<span style="color: lightpink;">_</span>' + s1 + '<span style="color: lightpink;">_</span>' + s2;
}

function colorEternaId(string) {
  string = string.split('_');
  s1 = '<span style="color: yellowgreen;">' + string[1] + '</span>';
  s2 = '<span style="color: skyblue;">' + string[2] + '</span>'; 
  return string[0] + '<span style="color: lightpink;">_</span>' + s1 + '<span style="color: lightpink;">_</span>' + s2;
}
