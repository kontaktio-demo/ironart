function rozwin(element){
	var rozwijane=element.getElementsByTagName('div');
	if(parseInt(rozwijane[0].style.height)==0 || rozwijane[0].style.height=="0px"){
		rozwijane[0].style.height=rozwijane[0].scrollHeight+"px";
	}else{
		rozwijane[0].style.height="0px";
	}
}