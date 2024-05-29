#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>

#define PORT 1337
#define MAX_CLIENTS 5

void handle_client(int new_socket){
   char buffer[1024] = {0};
   int valread = read(new_socket, buffer, 2048);
   //printf("Received: %s\n", buffer);
   send(new_socket, buffer, strlen(buffer), 0);
   printf("Message echo ok\n");
}

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[8] = {0};

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, MAX_CLIENTS) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    while (1) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("accept");
            exit(EXIT_FAILURE);
        }

        pid_t child_pid = fork();

        if (child_pid < 0) {
            perror("fork failed");
            exit(EXIT_FAILURE);
        }

        if (child_pid == 0) { 
           close(server_fd); 
           handle_client(new_socket);
           char *buf = "A last word ? :("; 
           send(new_socket, buf, strlen(buf), 0);
           read(new_socket, buffer, 8);
           close(new_socket);
           return 0;
        } else { 
            close(new_socket); 
        }
    }

   return 0;
}

