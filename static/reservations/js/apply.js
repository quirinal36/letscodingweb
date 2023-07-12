function searchList(btn){
    var searchTxt = document.getElementById('id_phone_number').value;

    window.location.href = "?phone_number="+searchTxt;
}

function userConfirm(msg){
    if (confirm(msg) == true){
        $.ajax({
            type:"POST", //post data
            data: $("form").serialize(), //if you want to send any data to view 
            url : $("form").attr("action"), // your url that u write in action in form tag
            dataType:"json",
            success: function(r){
                if(r.result == 'success'){    
                    parent.location.reload(true);
                }else{
                    console.log(r.message);
                }
            }
        })
        // $("form").submit();
    }else{
        return false;
    }
}

function page(num){
    
    $(location).attr('href', '?' + $("form").serialize()+"&page="+num);
}