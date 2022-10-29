# loki

Charmhub package name: loki
More information: https://charmhub.io/loki

## Deploying
Get the latest release from github and pass it as a resource to juju deployment.

    LOKI_VERSION=$(curl -s "https://api.github.com/repos/grafana/loki/releases/latest" | grep -Po '"tag_name": "v\K[0-9.]+')
    
    wget -qO loki.zip "https://github.com/grafana/loki/releases/download/v${LOKI_VERSION}/loki-linux-amd64.zip"
    
    juju deploy loki --resource loki-zipfile=./loki.zip --series jammy

## Setting a custom config with an action

    juju run-action loki/0 set-config config="$(base64 /tmp/loki.yaml)" --wait
