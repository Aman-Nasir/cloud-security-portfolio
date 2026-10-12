FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && curl -L -o /usr/local/bin/tfsec \
    https://github.com/aquasecurity/tfsec/releases/latest/download/tfsec-linux-amd64 \
 && chmod +x /usr/local/bin/tfsec \
 && pip install --no-cache-dir checkov

WORKDIR /scan
COPY *.tf /scan/

CMD ["sh", "-c", "echo '=== tfsec ===' && tfsec . ; echo '=== Checkov ===' && checkov -d . --framework terraform --compact"]