<?php

require_once $_SERVER['DOCUMENT_ROOT'] . '/vendor/autoload.php';


class Database {
    private static $instance;
    private $connection;

    private function __construct() {
	    $this->connection = new PDO("sqlite:/challenge/database.db");
    }

    public static function getInstance() {
        if (!self::$instance) {
            self::$instance = new Database();
        }
        return self::$instance;
    }

    public function getConnection() {
        return $this->connection;
    }
}
