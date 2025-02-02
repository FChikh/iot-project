FROM python:3.6-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
# COPY creds.json /usr/src/app/

RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir influxdb-client

COPY . /usr/src/app

COPY --from=shared_vol models.py /usr/src/app/swagger_server/controllers/models.py
COPY --from=shared_vol db.py /usr/src/app/swagger_server/controllers/db.py
#COPY ./shared_vol/models_db.py /app/swagger_server/controllers/models.py
#COPY ./shared_vol/db.py /app/swagger_server/controllers/db.py

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
