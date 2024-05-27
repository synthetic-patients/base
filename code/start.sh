#!/bin/sh

echo "Loading application in docker container..."
flask --app app.py run --host=0.0.0.0