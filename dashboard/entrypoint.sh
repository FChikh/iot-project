#!/bin/sh
python db_api.py &
streamlit run simulator_editor.py --server.port=8501 --server.address=0.0.0.0