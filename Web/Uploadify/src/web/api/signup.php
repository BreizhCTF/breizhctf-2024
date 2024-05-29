<?php

header("Content-Type: application/json");
if(isset($_SESSION["id"])) {
    echo json_encode(['status' => 'error', 'description' => 'Already logged in.']);
    exit();
}

if(isset($_POST['username']) && isset($_POST['password'])) {
    require_once '../utils/db.php';
    $result = register($_POST['username'], $_POST['password']);
    if($result) {
        echo json_encode(['status' => 'success']);
    } else {
        echo json_encode(['status' => 'error']);
    }
} else {
    echo json_encode(['status' => 'error', 'description' => 'Missing parameters.']);
}