# iot-project

Prerequisites:
1. create .env file containing the following environment variables
    ```shell
    MQTT_BROKER=mosquitto
    DOCKER_INFLUXDB_INIT_USERNAME={your influxdb username}   # Initial: admin
    DOCKER_INFLUXDB_INIT_PASSWORD={your influxdb password}   # Initial: admin123
    GF_SECURITY_ADMIN_USER={your grafana username}
    GF_SECURITY_ADMIN_PASSWORD={your grafana password}
    INFLUXDB_TOKEN={your token to access all the influx db's of your account}
    ```

2. create Google Calendar and enable the Google Calendar API
3. create service account for your Google Calendar API
4. Add service account with rights of making changes to the Google Calendar
5. create `env` folder and input the json file representing the credential of your service account on the Google Calendar API. The json credentials file need to be named `creds.json`



Building project:
```shell
sudo docker-compose build
```

To run:
```shell
docker-compose up
```

