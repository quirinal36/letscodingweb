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

function confirmApplication(msg, application_id){
    if (confirm(msg + " 하시겠습니까?")){
        $.ajax({
            type:"POST", //post data
            //data: $("form").serialize(), //if you want to send any data to view 
            url : '/reservation/application/confirm/'+application_id, // your url that u write in action in form tag
            dataType:"json",
            success: function(r){
                if(r.result == 'success'){    
                    parent.location.reload(true);
                }else{
                    console.log(r.message);
                }
            }
        })
    }
}


// django 의 csrf 토큰 문제를 해결하기 우해 필요함
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});