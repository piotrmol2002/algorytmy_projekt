# ====================================================================
# DOCKERFILE dla React Frontend
# ====================================================================

# Stage 1: Build
FROM node:18-alpine as build

WORKDIR /app

# Kopiuj package files
COPY package*.json ./

# Instaluj zależności
RUN npm install --legacy-peer-deps

# Kopiuj źródła
COPY . .

# Build produkcyjny
RUN npm run build

# Stage 2: Serwuj z nginx
FROM nginx:alpine

# Kopiuj build z poprzedniego stage
COPY --from=build /app/build /usr/share/nginx/html

# Kopiuj konfigurację nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]