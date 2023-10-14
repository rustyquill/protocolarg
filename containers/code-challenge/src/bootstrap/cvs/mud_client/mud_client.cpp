#include <iostream>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <openssl/bio.h>
#include <openssl/evp.h>

#define MAX_BUFFER_SIZE 4096

std::string base64Encode(const std::string &in) {
    BIO *bio, *b64;
    BUF_MEM *bufferPtr;

    b64 = BIO_new(BIO_f_base64());
    bio = BIO_new(BIO_s_mem());
    bio = BIO_push(b64, bio);

    BIO_write(bio, in.c_str(), in.length());
    BIO_flush(bio);

    BIO_get_mem_ptr(bio, &bufferPtr);
    BIO_set_close(bio, BIO_NOCLOSE);
    BIO_free_all(bio);

    std::string out(bufferPtr->data, bufferPtr->length);
    BUF_MEM_free(bufferPtr);
    return out;
}

int main(int argc, char *argv[]) {
    if(argc != 5) {
        std::cerr << "Usage: " << argv[0] << " <Server IP> <Server Port> <Username> <Password>\n";
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

    // Construct the credentials string and base64 encode it
    std::string credentials = std::string(argv[3]) + ":" + std::string(argv[4]);
    std::string encodedCredentials = base64Encode(credentials);

    // Send the credentials to the server
    send(sockfd, encodedCredentials.c_str(), encodedCredentials.size(), 0);

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
