#!/bin/sh

# Substitute environment variables in all HTML templates
echo "Processing HTML templates with environment variables..."

# Process each HTML file
for template in /tmp/*.html; do
    if [ -f "$template" ]; then
        filename=$(basename "$template")
        echo "Processing: $filename"
        
        envsubst '${OBSERVE_TENANT_ID} ${OBSERVE_STAGING_DOMAIN} ${OBSERVE_RUM_BEARER_TOKEN} ${OBSERVE_RUM_ENVIRONMENT} ${OBSERVE_RUM_SERVICE_NAME}' \
          < "$template" > "/usr/share/nginx/html/$filename"
    fi
done

# Make sure index.html exists (use index.html as main page)
if [ ! -f /usr/share/nginx/html/index.html ]; then
    echo "No index.html found, checking for alternatives..."
    if [ -f /usr/share/nginx/html/clean.html ]; then
        cp /usr/share/nginx/html/clean.html /usr/share/nginx/html/index.html
        echo "Using clean.html as index.html"
    fi
fi

echo "Environment variables substituted in HTML templates"
echo "OBSERVE_TENANT_ID: ${OBSERVE_TENANT_ID}"
echo "OBSERVE_RUM_ENVIRONMENT: ${OBSERVE_RUM_ENVIRONMENT}"
echo "OBSERVE_RUM_SERVICE_NAME: ${OBSERVE_RUM_SERVICE_NAME}"
echo "Available pages:"
ls -la /usr/share/nginx/html/*.html

# Execute the command passed to the container
exec "$@"