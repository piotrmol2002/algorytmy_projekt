# ====================================================================
# DOCKERFILE dla React Frontend
# ====================================================================

# Stage 1: Build
FROM node:16-alpine AS build

WORKDIR /app

# Kopiuj package files
COPY package.json ./

# Instaluj zależności (bez package-lock żeby npm sam rozwiązał konflikty)
RUN npm install --legacy-peer-deps

# Kopiuj źródła
COPY . .

# Build produkcyjny
ENV DISABLE_ESLINT_PLUGIN=true
ENV CI=false
RUN npm run build

# Stage 2: Serwuj z nginx
FROM nginx:alpine

# Kopiuj build z poprzedniego stage
COPY --from=build /app/build /usr/share/nginx/html

# Kopiuj konfigurację nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]