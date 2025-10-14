FROM nginx:alpine

# Kopiuj index.html
COPY index.html /usr/share/nginx/html/

# Kopiuj konfigurację nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]