function deleteEvent(eventId){
    
    $("<div></div>").appendTo('body')
    .attr("id", "dialog")
    .html('<div><h3>정말 이 글을 삭제하시겠습니까?</h3></div>')
    .dialog({
        title: "식제" ,
        width:500, height:140,
        modal:true,
        resizable: false, 
        show: { effect: 'drop', direction: "left" }, 
        hide: { effect:'blind' },
        buttons: {
            Yes: function() {
                $.ajax({
                    type:"POST", //post data
                    // data:{'key':key}, //if you want to send any data to view 
                    url:'/reservation/event/delete/'+eventId, // your url that u write in action in form tag
                    dataType:"json",
                    success: function(r){
                        if(r.result == 'success'){    
                            parent.location.reload(true);
                        }else{
                            console.log(r.message);
                        }
                    }
                })
            },
            Cancel: function() {
                $( this ).dialog( "close" );
            }
        }
    });  
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

$(".event-delete").each(function(i, button) {
    button.attr("onclick", deleteEvent(button.val()));
});