$(function(){
    $('.search_option').change(function(){
        $(location).attr('href', '?'+ $("#eduList").serialize());
    });
});

function page(num){
    console.log("num:" + num)
    
    $(location).attr('href', '?' + $("#eduList").serialize()+"&page="+num);
}