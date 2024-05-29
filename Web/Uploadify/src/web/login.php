<?php


if(isset($_SESSION["id"])) {
    header('Location: /');
    exit();
}

require_once 'vendor/autoload.php';

$loader = new \Twig\Loader\FilesystemLoader('templates');
$twig = new \Twig\Environment($loader);

echo $twig->render('login.twig');