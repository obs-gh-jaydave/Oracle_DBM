#!/bin/sh

# Substitute environment variables in the HTML template
envsubst '${OBSERVE_TENANT_ID} ${OBSERVE_STAGING_DOMAIN} ${OBSERVE_RUM_BEARER_TOKEN} ${OBSERVE_RUM_ENVIRONMENT} ${OBSERVE_RUM_SERVICE_NAME}' \
  < /tmp/clean.html.template > /usr/share/nginx/html/index.html

echo "Environment variables substituted in HTML template"
echo "OBSERVE_TENANT_ID: ${OBSERVE_TENANT_ID}"
echo "OBSERVE_RUM_ENVIRONMENT: ${OBSERVE_RUM_ENVIRONMENT}"
echo "OBSERVE_RUM_SERVICE_NAME: ${OBSERVE_RUM_SERVICE_NAME}"

# Execute the command passed to the container
exec "$@"