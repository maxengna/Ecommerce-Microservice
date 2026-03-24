FROM node:23-alpine AS builder
WORKDIR /app

# Copy package.json เข้าไปใน Container เพื่อติดตั้ง Package ต่างๆ
COPY package.json ./

# ติดตั้ง Package ต่างๆที่ต้องใช้
RUN npm install

# Copy code ส่วนที่เหลือเช้าไปใน Container
COPY . .

# Build Next application
RUN npm run build

# เราควรจะใช้ Base Image ตัวเดียวกับ Builder ตัวก่อนหน้าเพื่อไม่ให้มีปัญหาเรื่อง Version
FROM node:23-alpine AS runner
WORKDIR /app

# ติดตั้ง Next CLI
# RUN npm install -g next

# Install curl for health check
RUN apk add --no-cache curl

# กำหนด Environment เป็น Production
ENV NODE_ENV=production

# Create non-root user and logs directory
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
RUN mkdir -p /app/logs && chown nextjs:nodejs /app/logs

# Copy output จาก Builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public/ ./public/

# Change ownership to non-root user
RUN chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start Next application
CMD ["npm", "run", "start"]