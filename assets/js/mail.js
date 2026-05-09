function mailto(id){
	var czesci=Array('>','a','/','<','l','p','.','m','o','c','.','e','n','z','c','y','t','s','y','t','r','a','-','o','w','t','s','l','a','w','o','k',String.fromCharCode(64),'>','"','l','p','.','m','o','c','.','e','n','z','c','y','t','s','y','t','r','a','-','o','w','t','s','l','a','w','o','k',String.fromCharCode(64),':','o','t','l','i','a','m','"','=','f','e','r','h',' ','a','<');
	czesci.reverse();
	var str='';
	var m=id;
	var maile=document.getElementsByClassName('mail');
	for(a=0;a<maile.length;a++){
		str='';
		m=id;
		if(maile[a].getAttribute('name')!=undefined && maile[a].getAttribute('name')!='')m=maile[a].getAttribute('name');
		for(b=0;b<czesci.length;b++){
			if(czesci[b]==String.fromCharCode(64))str+=(m+czesci[b]);
			else str+=czesci[b];
		}			
		
		maile[a].innerHTML+=str;
	}
}
window.onload=function(){
	mailto('biuro');
}