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
            <li class="nav-item">
                <a class="nav-link" href="/rate">Rate</a>
            </li>
            <li class="nav-item active">
                <a class="nav-link" href="#">Bugs <span class="sr-only">(current)</span></a>
            </li>
        </div>
    </nav>
    <div class="container">
        <div class="row">
            <div class="col text-center">
                <p class="lead">List of known bugs: </p>
                <table class="table table-dark">
                    <thead>
                        <tr>
                        <th scope="col">#</th>
                        <th scope="col">Bug Type</th>
                        <th scope="col">CVSS</th>
                        <th scope="col">Researcher</th>
                        <th scope="col">Fix</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <th scope="row">1</th>
                            <td>SSRF (Server Side Request Forgery)</td>
                            <td>10</td>
                            <td>Kaluche</td>
                            <td>❌</td>
                        </tr>
                        <tr>
                            <th scope="row">2</th>
                                <td>Possibility to fetch local files of server</td>
                                <td>7.5</td>
                                <td>SaxX</td>
                                <td>✅</td>
                            </tr>
                        <tr>
                            <th scope="row">3</th>
                                <td>Malformed title tag is not take into account</td>
                                <td>Not applicable</td>
                                <td>Internal Dev Team</td>
                                <td>❌</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>