CREATE TABLE `users` (
  `id` INTEGER PRIMARY KEY,
  `username` varchar(255) NOT NULL UNIQUE,
  `password` varchar(255) NOT NULL
); 

CREATE TABLE `files` (
    `id` INTEGER PRIMARY KEY,
    `user_id` int(11) NOT NULL,
    `name` varchar(255) NOT NULL,
    `path` varchar(255) NOT NULL,
    `private` tinyint(1) NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
);

INSERT INTO `users`(username, password) VALUES ('admin', '$2y$10$jD9HiyOhXFMalrh4LK4MruqKlzI2.vuW3GcmV53386Q2mNtGmNhLy');
INSERT INTO `files`(user_id, name, path, private) VALUES (1, 'flag', '/flag.txt', 1);
