function searchList(btn){
    var searchTxt = document.getElementById('id_phone_number').value;

    window.location.href = "?phone_number="+searchTxt;
}