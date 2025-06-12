FROM nginx:alpine

# Copy all HTML files as templates
COPY *.html /tmp/

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Install gettext for envsubst
RUN apk add --no-cache gettext

# Copy startup script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]