<?php

require_once $_SERVER["DOCUMENT_ROOT"] . "/config.php";

function register($username, $password): bool
{
    $pdo = Database::getInstance()->getConnection();
    $password_hash = password_hash($password, PASSWORD_DEFAULT);

    try {
        $stmt = $pdo->prepare("INSERT INTO users (username, password) VALUES (:u, :p)");
	$stmt->bindParam(':u', $username);
	$stmt->bindParam(':p', $password_hash);
        $stmt->execute();
    } catch(Exception $e) {
	    return false;
    }
    return true;
}

function login($username, $password) {
    $pdo = Database::getInstance()->getConnection();
    $stmt = $pdo->prepare('SELECT * FROM users WHERE username = :u');
    $stmt->bindParam(':u', $username);
    $stmt->execute();
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    if ($user && password_verify($password, $user['password'])) {
        return $user['id'];
    }
    return false;
}

function get_file($id, $user_id) {
    $pdo = Database::getInstance()->getConnection();
    $stmt = $pdo->prepare('SELECT * FROM files WHERE id = :i AND (user_id = :ui OR private = 0)');
    $stmt->bindParam(':i', $id);
    $stmt->bindParam(':ui', $user_id);
    $stmt->execute();
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function get_files($user_id) {
    $pdo = Database::getInstance()->getConnection();
    $stmt = $pdo->prepare('SELECT * FROM files WHERE user_id = :i');
    $stmt->bindParam(':i', $user_id);
    $stmt->execute();
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function add_file($user_id, $name, $filename, $private) {
    $pdo = Database::getInstance()->getConnection();
    $stmt = $pdo->prepare('INSERT INTO files (user_id, name, path, private) VALUES (:ui, :n, :p, :private)');
    $stmt->bindParam(':ui', $user_id);
    $stmt->bindParam(':n', $name);
    $stmt->bindParam(':p', $filename);
    $stmt->bindParam(':private', $private);
    $stmt->execute();
}
