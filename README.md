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

## Testing Loki listens and recieves logs

    curl -H "Content-Type: application/json" -XPOST -s "http://localhost:3100/loki/api/v1/push" --data-raw "{\"streams\": [{\"stream\": {\"job\": \"test\"}, \"values\": [[\"$(date +%s)000000000\", \"fizzbuzz\"]]}]}"

    curl -G -s "http://localhost:3100/loki/api/v1/query_range" --data-urlencode 'query={job="test"}' --data-urlencode 'step=300' | jq .data.result

Should print something like

```
[
  {
    "stream": {
      "job": "test"
    },
    "values": [
      [
        "1667681980000000000",
        "fizzbuzz"
      ],
      [
        "1667680893000000000",
        "fizzbuzz"
      ],
      [
        "1667680876000000000",
        "fizzbuzz"
      ],
      [
        "1667680844000000000",
        "fizzbuzz"
      ]
    ]
  }
]

```
