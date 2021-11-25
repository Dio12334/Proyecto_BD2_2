function refactor()
{
    let theme = $('#theme').val();
    theme = theme.toString()

    let mydata = {
        "theme": theme,
        "maxtweets": $('#numbert').val()
    }
    mydata = JSON.stringify(mydata);

    $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: "application/json",
        data: mydata,
        url: '/changeindex',
        success: function() {
            alert('New Data create');
        }
    })
}
function search()
{
    let search = $('#search').val();
    search = search.toString()

    let mydata = {
        "search": search,
        "k": $('#k').val()
    }
    mydata = JSON.stringify(mydata);

    $.ajax({
        type: 'POST',
        dataType: 'json',
        contentType: "application/json",
        data: mydata,
        url: '/search',
        success: function() {
            location.reload();
        }
    })
}