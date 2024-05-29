#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>

#define MAX_CLIENTS 50
#define BUFFER_SIZE 0x50
#define PORT 1337

pthread_t threads[MAX_CLIENTS];

ssize_t recv_bytes = 0;

void exec_command(int client_sockfd, char *command){
    char buffer[1024];
    memset(buffer,0,1024);
    //send(client_sockfd, "Yeah\n", 6, 0);

    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        printf("Failed to run command\n");
        //exit(1);
    }

    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        send(client_sockfd, buffer, sizeof(buffer), 0);
    }

    // dup2(client_sockfd,0);
    // dup2(client_sockfd,1);
    // system(command);
}

void *handle_client(void *arg) {
    int client_sockfd = *((int *)arg);
    char buffer[BUFFER_SIZE];

    while ((recv_bytes = recv(client_sockfd, buffer, BUFFER_SIZE, 0)) > 0) {
        sleep(1);
        //if (recv_bytes > 1){
        if (recv_bytes == 1){
            exec_command(client_sockfd,buffer);
            break;
        } else {
            send(client_sockfd, "Nop\n", 4, 0);
        }
        memset(buffer,0,BUFFER_SIZE);
    }

    if (recv_bytes == -1) {
        perror("recv");
    }
    close(client_sockfd);    
    //pthread_exit(NULL);
}

int main() {
    setbuf(stdout, 0);
    int sockfd, client_sockfd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len = sizeof(client_addr);

    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt failed");
        return 1;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(PORT);

    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind");
        exit(EXIT_FAILURE);
    }

    // Listen for incoming connections
    if (listen(sockfd, MAX_CLIENTS) == -1) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", PORT);

    int i = 0;
    while (1) {
        if ((client_sockfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_addr_len)) == -1) {
            perror("accept");
            continue;
        }

        //printf("Connection accepted from %s:%d\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        if (pthread_create(&threads[i++], NULL, handle_client, &client_sockfd) != 0) {
            perror("pthread_create");
            continue;
        }
    }

    close(sockfd);
    return 0;
}
