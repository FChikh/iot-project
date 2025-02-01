#!/bin/sh
# Start the REST API in the background.
python global_config.py &

# Start the Streamlit dashboard in the foreground.
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0