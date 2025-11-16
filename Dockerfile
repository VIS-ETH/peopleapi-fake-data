FROM python:3-alpine

COPY user-generator /app

WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

COPY global-fake-data /data

COPY --chmod=777 <<EOF run.sh
#!/bin/sh
set -euo pipefail

python3 main.py --seed 501298 -n 100 -o json > /data/users.json
mv /data/* /mnt/import
EOF

CMD [ "/app/run.sh" ]
