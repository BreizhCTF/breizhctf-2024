<?php

session_start();

require_once __dir__ . '/../vendor/autoload.php';

require_once __dir__ . '/../utils/db.php';

if(isset($_GET["id"])) {
    $loader = new \Twig\Loader\FilesystemLoader(__dir__ . '/../templates');
    $twig = new \Twig\Environment($loader);

    $file = get_file($_GET["id"], $_SESSION["id"])[0];
    if($file) {
        $file_path = $file["path"];
        $headers = "Content-Type: application/octet-stream\r\nContent-Disposition: attachment; filename=\"" . $file["name"] . '"';
        if(file_exists($file_path)) {
            $headers = explode("\r\n", $headers);
            foreach($headers as $header) {
                header($header);
            }
            echo file_get_contents($file_path);
            exit();
        }
    }
    // echo $twig->render('home.twig', ["message" => "File not found"]);
} else {
    header('Location: /home.php');
    exit();
}
