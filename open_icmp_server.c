/* open_icmp_server.c -- minimal ICMP echo responder (root or CAP_NET_RAW required) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/ip_icmp.h>
#include <errno.h>

static volatile sig_atomic_t running = 1;

static void handle_sigint(int sig) { (void)sig; running = 0; }

static unsigned short checksum(void *b, int len) {
  unsigned short *buf = b;
  unsigned int sum = 0;
  unsigned short result;
  
  for (sum = 0; len > 1; len -= 2)
      sum += *buf++;
  if (len == 1)
      sum += *(unsigned char*)buf;
  sum = (sum >> 16) + (sum & 0xffff);
  sum += (sum >> 16);
  result = ~sum;
  return result;

}

int main(void) {
  int sockfd;
  ssize_t n;
  char buf[1500];
  struct sockaddr_in addr;
  socklen_t addrlen = sizeof(addr);

  signal(SIGINT, handle_sigint);
  signal(SIGTERM, handle_sigint);
  
  sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
  if (sockfd < 0) {
      perror("socket");
      return 1;
  }
  
  fprintf(stderr, "open-icmp-server (C): started\n");
  
  while (running) {
      n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr*)&addr, &addrlen);
      if (n <= 0) {
          if (errno == EINTR) continue;
          perror("recvfrom");
          break;
      }
      if (n < (ssize_t)sizeof(struct icmphdr)) continue;
  
      struct icmphdr *icmp = (struct icmphdr*)buf;
      if (icmp->type == ICMP_ECHO) {
          struct icmphdr reply = {0};
          reply.type = ICMP_ECHOREPLY;
          reply.code = 0;
          reply.un.echo.id = icmp->un.echo.id;
          reply.un.echo.sequence = icmp->un.echo.sequence;
  
          memcpy(buf, &reply, sizeof(reply));
  
          ((struct icmphdr*)buf)->checksum = 0;
          ((struct icmphdr*)buf)->checksum = checksum(buf, n);
  
          if (sendto(sockfd, buf, n, 0, (struct sockaddr*)&addr, addrlen) < 0) {
              perror("sendto");
          } else {
              char ipstr[INET_ADDRSTRLEN];
              inet_ntop(AF_INET, &addr.sin_addr, ipstr, sizeof(ipstr));
              fprintf(stderr, "Replied to %s (len=%zd)\n", ipstr, n);
          }
      }
  }
  
  close(sockfd);
  fprintf(stderr, "open-icmp-server (C): stopping\n");
  return 0;

}
