FROM postgres:16-alpine

# ตั้งค่า env พื้นฐาน
ENV POSTGRES_DB=appdb \
    POSTGRES_USER=appuser \
    POSTGRES_PASSWORD=securepassword \
    PGDATA=/var/lib/postgresql/data/pgdata

# copy init script (optional)
COPY ./init-db.sql /docker-entrypoint-initdb.d/

# copy custom config (ถ้ามีไฟล์ postgresql.conf)
COPY ./postgresql.conf /etc/postgresql/postgresql.conf

# สร้าง log directory
RUN mkdir -p /var/log/postgresql && chown postgres:postgres /var/log/postgresql

# expose port
EXPOSE 5432

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pg_isready -U appuser -d appdb || exit 1

# ใช้ custom config
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]