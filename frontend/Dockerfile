# Используем легковесный образ Node.js
FROM node:20-alpine

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Копируем исходный код
COPY . .

# Открываем порт 3000 (указан в docker-compose.yml)
EXPOSE 3000

# Запускаем Vite с пробросом порта и хоста
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]