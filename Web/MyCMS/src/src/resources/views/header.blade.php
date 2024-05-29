<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MyCMS</title>
  <!-- Liaison avec Bootstrap CSS -->
  <link href="{{secure_asset('css/bootstrap.min.css')}}" rel="stylesheet">
  <style>
    /* Pour ajuster la hauteur de la page */
    body {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    /* Pour centrer le contenu */
    .container {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
    }
  </style>
  <script src="{{secure_asset('js/jquery-3.5.1.min.js')}}"></script>
  <script src="{{secure_asset('js/bootstrap.min.js')}}"></script>
  <script src="{{secure_asset('js/popper.min.js')}}"></script>
</head>
<body>