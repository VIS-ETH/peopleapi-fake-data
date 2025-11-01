# peopleapi-fake-data

```bash
curl -H "Authorization: Basic $(echo -n 'ei-tool:ei-tool' | base64 -w0)" -X POST https://keycloak-fake.vis.ethz.ch/realms/VSETH/protocol/openid-connect/token --data-urlencode "grant_type=client_credentials" | yq -r '.access_token'
```
