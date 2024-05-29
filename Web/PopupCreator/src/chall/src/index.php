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
            <li class="nav-item active">
                <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/rate">Rate</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/bugs">Bugs</a>
            </li>
        </div>
    </nav>
    <div class="container">
        <div class="row">
            <div class="col text-center">
                <p class="lead">Welcome on "Popup Website Creator", this website aims to create popup for embed links to display the title and images of a website !</p>
                <p>As this is an alpha version, please report any bug to "wedontcare@bullshit.corp" (check <a href="/bugs">here</a> for known bugs), for now, it's free to use !</p>
                <p><a href="/rate">Click here</a> to test our new tool !</p>
                <img src="/images/index.png"></img>
            </div>
        </div>
    </div>
</body>