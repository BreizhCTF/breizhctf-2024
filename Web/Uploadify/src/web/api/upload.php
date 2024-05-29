<?php

session_start();

require_once __dir__ . '/../utils/db.php';

if(!isset($_SESSION["id"])) {
    http_response_code(403);
    die('Forbidden');
}

if(!isset($_FILES['file'])) {
    header("Location: /home.php?message=Error");
    echo json_encode(['status' => 'Missing parameters.']);
} else {
    // handle file upload
    header("Location: /home.php?message=Success");
    $target_dir = "/tmp/uploads/";
    if(!is_dir($target_dir)) {
	mkdir($target_dir);
    }
    $name = urldecode($_FILES['file']['name']);
    $private = 0;
    if(isset($_POST["private"]))
        $private = $_POST["private"] == "on" ? 1 : 0;

    // get random filename
    $filename = bin2hex(random_bytes(16));
    file_put_contents($target_dir . $filename, file_get_contents($_FILES['file']['tmp_name']));

    add_file($_SESSION["id"], $name, $target_dir . $filename, $private);
}

