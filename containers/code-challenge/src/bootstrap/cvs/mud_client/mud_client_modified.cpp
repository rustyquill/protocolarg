#include <iostream>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

#define MAX_BUFFER_SIZE 4096

int main(int argc, char *argv[]) {
    if(argc != 3) {
        std::cerr << "Usage: " << argv[0] << "tnet.office-of-incident-assessment-and-response.org.uk 10023\n";
        exit(EXIT_FAILURE);
    }

    // Create a socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if(sockfd < 0) {
        std::cerr << "Failed to create socket.\n";
        exit(EXIT_FAILURE);
    }

    // Setup server details
    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(atoi(argv[2])); // Server port

    // Convert IPv4 and IPv6 addresses from text to binary form
    if(inet_pton(AF_INET, argv[1], &serv_addr.sin_addr) <= 0) {
        std::cerr << "Failed to setup server address.\n";
        exit(EXIT_FAILURE);
    }

    // Connect to the server
    if(connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "Connection failed.\n";
        exit(EXIT_FAILURE);
    }

    char buffer[MAX_BUFFER_SIZE];
    memset(buffer, 0, sizeof(buffer));

    std::cout << "Connected to the server. Type your message and press enter to send:\n";

    while(true) {
        std::cout << ">> ";
        std::cin.getline(buffer, MAX_BUFFER_SIZE);

        send(sockfd, buffer, sizeof(buffer), 0);

        memset(buffer, 0, sizeof(buffer));
        recv(sockfd, buffer, sizeof(buffer), 0);
        std::cout << "Server: " << buffer << "\n";
    }

    close(sockfd);
    return 0;
}
