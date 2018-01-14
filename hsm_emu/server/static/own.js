
function highlight(id){
	jQuery("div#navbar li.active").removeClass('active');          
  	jQuery(id).addClass('active');
}

function openInNewTab(url) {
  var win = window.open(url, '_blank');
  //win.focus();
}
