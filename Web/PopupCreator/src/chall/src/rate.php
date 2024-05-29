<?php
session_start();
?>
<!DOCTYPE HTML>
<head>
    <title>Popup Website Creator</title>
    <link rel="stylesheet" href="/static/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    <script src="/static/jquery-3.3.1.min.js" crossorigin="anonymous"></script>
    <script src="/static/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
    <script src="/static/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="#">Popup Website Creator</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav mr-auto">
            <li class="nav-item">
                <a class="nav-link" href="/">Home</a>
            </li>
            <li class="nav-item active">
                <a class="nav-link" href="#">Rate  <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/bugs">Bugs</a>
            </li>
        </div>
    </nav>
    <div class="container">
        <div class="row">
            <div class="col text-center">
                <p class="lead">Let's create your popup !</p>
                    <div class="form-group mx-sm-3 mb-2">
                        <input type="URL" class="form-control" id="url" placeholder="https://www.google.com">
                    </div>
                    <input type="button" class="btn btn-primary mb-2" value="Go!" readonly onclick="fetch_website()" />
                    <div id="popup" class="row align-items-center justify-content-center"></div>
            </div>
        </div>
    </div>
    <script>
        function fetch_website()
        {
            $("#popup").empty();
            var request = $.ajax({
                url: "/fetch",
                type: "POST",
                data: {"url": $("#url").val()},
                dataType: "json"
            });

            request.done(function(msg){
                if(msg['data'] != undefined)
                {
                    $("#popup").append(`<div class="card" style="width: 18rem;"><img class="card-img-top" src="data:image/png;base64, ${msg['data']['image']}"><div class="card-body"><h5 class="card-title">${msg['data']['title']}</h5><p class="card-text">Here is an example of the popup created with data of your website !</p></div></div>`);
                    if(msg['data']['image2'] != undefined)
                    {
                        $("#popup").append(`<div class="card" style="width: 18rem;"><img class="card-img-top" src="data:image/png;base64, ${msg['data']['image2']}"><div class="card-body"><h5 class="card-title">${msg['data']['title']}</h5><p class="card-text">Here is an example of the popup created with data of your website !</p></div></div>`);
                    }
                }
                else
                {
                    alert(msg['error']);
                }
            })

            request.fail(function(_, msg){
                alert("Network error.");
            })
        }
    </script>
</body>