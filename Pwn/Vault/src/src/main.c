#include<stdio.h>
#include<string.h>    //strlen
#include<stdlib.h>    //strlen
#include<sys/socket.h>
#include<arpa/inet.h> //inet_addr
#include<unistd.h>    //write
#include<pthread.h> //for threading , link with lpthread

void *connection_handler(void *);

int main(){
  int socket_desc , client_sock , c;
  struct sockaddr_in server , client;
  setbuf(stdout, 0);
  socket_desc = socket(AF_INET , SOCK_STREAM , 0);
  if (socket_desc == -1)
  {
      printf("Could not create socket");
  }
  puts("Socket created");
   
  int opt = 1;
  if (setsockopt(socket_desc, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
      perror("setsockopt failed");
      return 1;
  }

  server.sin_family = AF_INET;
  server.sin_addr.s_addr = INADDR_ANY;
  server.sin_port = htons( 1337 );
   
  if( bind(socket_desc,(struct sockaddr *)&server , sizeof(server)) < 0)
  {
      perror("bind failed. Error");
      return 1;
  }
  puts("bind done");
   
  listen(socket_desc , 3);
   
  puts("Waiting for incoming connections...");
  c = sizeof(struct sockaddr_in);
  pthread_t thread_id;

  while( (client_sock = accept(socket_desc, (struct sockaddr *)&client, (socklen_t*)&c)) )
  {
      puts("Connection accepted");
       
      if( pthread_create( &thread_id , NULL ,  connection_handler , (void*) &client_sock) < 0)
      {
          perror("could not create thread");
          return 1;
      }
      puts("Handler assigned");
  }
   
  if (client_sock < 0)
  {
      perror("accept failed");
      return 1;
  }

  return 0;
}

char *create_temp_vault(int fd){
  
  uint32_t len = 0;
  char inp[8];
  char *s_str = "Size ?\n";
  write(fd, s_str,strlen(s_str));
  uint8_t read_len = read(fd,inp,8); 
  
  len = atoi(inp);

  char *buffer = alloca(len);
  len = read(fd,buffer,len);
  buffer[len-1] = 0;

  //printf("buff addr : %p\n",buffer);
  return buffer;
}

void *connection_handler(void *socket_desc)
{
  //Get the socket descriptor
  int fd = *(int*)socket_desc;
  int read_size;
  char *message , client_message[8];
  int choice;
  int len = 0;
  char *buff;
  //Send some messages to the client
  message = "\n--- [ Temp vault for copy paste ] ---\n1. create temp vault\n2. read temp vault\n3. exit\n: ";
  write(fd , message , strlen(message));
   
  while( (read_size = recv(fd , client_message , 2 , 0)) > 0 )
  {
     choice = atoi(client_message);
     if (choice==1) {
      buff = create_temp_vault(fd);
    } else if(choice==2){
      if (buff){
        len = strlen(buff);
        write(fd , buff , len);
        write(fd,"\n",1);
      }
    } else if(choice==3){
      break;
    }
    
    write(fd , message , strlen(message));
  }

  close(fd);
  return 0;
}
