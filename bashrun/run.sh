#!/bin/bash

cd /path/to/your/app
python app.py &
sleep 5
xdg-open http://0.0.0.0:8000
