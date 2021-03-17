#! /bin/sh

#Create AAI STORAGE Space
mkdir -p ~/AAI_FILES/STORAGE_SPACE

# Run docker containers
echo "Run docker containers"
docker-compose up -d

echo "Wait for docker instantiation 40 seconds"
sleep 40

# Send CBA Files

cd Microwave_ONAP

./send_cba.sh

cd ..

echo "Wait for template installation"

# Init Project

./init_project.sh



