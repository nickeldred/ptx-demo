# Base Image
FROM nginx:latest

# App Files
COPY index.html /usr/share/nginx/html/index.html

# Nginx Port 80
EXPOSE 80
