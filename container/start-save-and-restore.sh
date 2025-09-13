set -x

python create_env_file.py
sudo docker compose -f save-and-restore.yml up -d

# Wait until the service is started.
sleep 30
