function ustawCookie(nazwa, wartosc, expire){
	document.cookie = nazwa + "=" + escape(wartosc) + ((expire==null)?"" : ("; expires=" + expire.toGMTString()))
}
function zamknij_ciasteczko(){
	var waznosc = new Date();
	waznosc.setMonth(waznosc.getMonth()+144);
	ustawCookie('ciasteczko','1',waznosc);
	document.getElementById('cookies').style.display='none';
}
var gdzie = document.cookie.indexOf('ciasteczko=');
if(document.cookie.substr(gdzie+11,1)=='1'){
	document.getElementById('cookies').style.display='none';	
};