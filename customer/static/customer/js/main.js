function alert_box(id, name) {
	var box = confirm("Sure you want to delete the bill of "+name+"?")
	if(box){
    	window.location.replace("/customer/delete-bill/"+id+"/")
	}
}