FROM redis:7.0.11-alpine
WORKDIR /redis
COPY redis.conf /usr/local/etc/redis/redis.conf
COPY init.sh ./
RUN chmod +x init.sh
CMD ["sh", "-c", "./init.sh"]
