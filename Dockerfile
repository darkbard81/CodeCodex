# Step 1: 빌드용 이미지 (tsc 컴파일)
FROM node:18 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY tsconfig.json ./
COPY src ./src

RUN npx tsc

# Step 2: 실행용 이미지 (최소화)
FROM node:18-slim

WORKDIR /app

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/dist ./dist
RUN npm install --omit=dev

EXPOSE 3000

CMD ["node", "dist/index.js"]
