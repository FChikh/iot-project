# dashboard/Dockerfile

FROM python:3.9-slim

WORKDIR /app
RUN mkdir /app/pages

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY streamlit_app.py /app/
COPY pages /app/pages
COPY db.py /app/
COPY global_config.py /app/
COPY entrypoint.sh /app/
COPY requirements.txt /app/
COPY simulator.py /app/
COPY --from=configs ./models.py /app/
COPY --from=configs ./config.json /app/

RUN chmod +x /app/entrypoint.sh

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
EXPOSE 9999

CMD ["/app/entrypoint.sh"]