FROM postgres:17

COPY docker/init.sql /docker-entrypoint-initdb.d/