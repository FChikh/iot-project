# IoT-Based Decision Support System for Room Selection
This project focuses on optimizing room selection by ranking rooms based on sensor data, user preferences, and compliance with EU regulations. 
It includes a decision-making system, a sensor simulation interface, a dashboard for monitoring, and a booking system.

Presentation is available [here](iot-project-slides.pdf), technical report can be found [here](report.pdf).

Developed by [Fedor Chikhachev](https://github.com/FChikh), [Vladyslav Siulhin](https://github.com/SiulhinVlad), [Thuc Kevin Nguyen](https://github.com/Thuctac), and [Tarik Tornes](https://github.com/TarikTornes), this project provides a comprehensive solution for managing and utilizing room resources efficiently.

## Key-features
- Decision System: Ranks rooms by analyzing sensor data, user preferences, and regulatory compliance.
- Sensor Simulation: Simulates various room sensors for testing and validation.
- Dashboard: Displays real-time metrics and insights for administrators.
- Booking System: Manages room reservations through integration with Google Calendar.
- Management: Enables admin to observe and manage data effectively.

This system is designed to support both administrators in monitoring room conditions and users in finding/booking suitable rooms.

## Prerequisites
1. create .env file containing the following environment variables
    ```shell
    MQTT_BROKER=mosquitto
    DOCKER_INFLUXDB_INIT_USERNAME={your influxdb username}   # Initial: admin
    DOCKER_INFLUXDB_INIT_PASSWORD={your influxdb password}   # Initial: admin123
    GF_SECURITY_ADMIN_USER={your grafana username}
    GF_SECURITY_ADMIN_PASSWORD={your grafana password}
    INFLUXDB_TOKEN={your token to access all the influx db's of your account}
    MQTT_BROKER=mosquitto

    POSTGRES_USER={your username for postgres}
    POSTGRES_PASSWORD={your password for postgres}
    POSTGRES_DB=rooms_db
    POSTGRES_HOST=postgres
    POSTGRES_PORT=5432
    ```

2. create Google Calendar and enable the Google Calendar API
3. create service account for your Google Calendar API
4. Add service account with rights of making changes to the Google Calendar
5. create `env` folder and input the json file representing the credential of your service account on the Google Calendar API. The json credentials file need to be named `creds.json`


## Running the System

Building project:
```shell
sudo docker-compose build
```

To run:
```shell
docker-compose up
```


