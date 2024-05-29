<?php
session_start();

header("Content-Type: application/json");

if(isset($_POST['username']) && isset($_POST['password'])) {
    require_once '../utils/db.php';
    $id = login($_POST['username'], $_POST['password']);
    if($id) {
        $_SESSION['id'] = $id;
        echo json_encode(['status' => 'success']);
    } else {
        echo json_encode(['status' => 'error']);
    }
} else {
    echo json_encode(['status' => 'Missing parameters.']);
}