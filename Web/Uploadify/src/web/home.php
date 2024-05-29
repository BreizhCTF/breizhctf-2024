<?php

session_start();

if(!isset($_SESSION["id"])) {
    header('Location: /');
    exit();
}

$message = isset($_GET['message']) ? $_GET['message'] : '';

require_once __dir__ . '/vendor/autoload.php';
require_once __dir__ . '/utils/db.php';

$loader = new \Twig\Loader\FilesystemLoader('templates');
$twig = new \Twig\Environment($loader);

$files = get_files($_SESSION["id"]);
echo $twig->render('home.twig', ['files' => $files, 'message' => $message]);
//var_dump($files);
?>
