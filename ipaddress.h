#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/**
 * if std operation in posix based OS 
 * include<unistd.h>
*/
#if defined (__linux__)
    #include <unistd.h>
#endif


int count_ones(uint32_t num) {
    int count;
    asm (
        "popcnt %1, %0"
        : "=r" (count)
        : "r" (num)
    );
    return count;
}

uint32_t CalC_Host(const char *subnet_mask) {
    uint32_t mask = Inet_To_Int(subnet_mask);
    if (mask == 0) {
        printf("Invalid subnet mask\n");
        return 0;
    }
    int ones = count_ones(mask);
    int host_bits = 32 - ones; 

    uint32_t number_of_hosts;
    asm (
        "movl $1, %0\n"
        "shll %1, %0\n"
        "subl $2, %0"
        : "=r" (number_of_hosts)
        : "r" (host_bits)
    );
    return number_of_hosts;
}


uint32_t Inet_To_Int(const char *ip_str) {
    uint32_t ip = 0;
    int octet;
    char *token;
    char ip_copy[16];

    strncpy(ip_copy, ip_str, sizeof(ip_copy));
    ip_copy[sizeof(ip_copy) - 1] = '\0';

    token = strtok(ip_copy, ".");
    for (int i = 0; i < 4; i++) {
        if (token != NULL) {
            octet = atoi(token);
            asm (
                "shl $8, %0\n"
                "or %1, %0"
                : "=r" (ip)
                : "r" ((uint32_t)octet & 0xFF), "0" (ip)
            );
            token = strtok(NULL, ".");
        } else {
            return 0; 
        }
    }

    return ip;
}

int isNetworkOf(const char *ip1, const char *ip2, const char *subnet_mask) {
    uint32_t addr1 = Inet_To_Int(ip1);
    uint32_t addr2 = Inet_To_Int(ip2);
    uint32_t mask = Inet_To_Int(subnet_mask);

    if (addr1 == 0 || addr2 == 0 || mask == 0) {
        printf("Invalid IP address or subnet mask\n");
        return 0;
    }

    uint32_t net1, net2;
    asm (
        "andl %2, %1\n"
        "andl %2, %3\n"
        : "=r" (net1), "=r" (net2)
        : "r" (mask), "1" (addr1), "3" (addr2)
    );

    return net1 == net2;
}
