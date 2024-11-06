#!/bin/bash

# Default values
ENV="development"
HOST="0.0.0.0"
PORT="4439"
DEBUG="true"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env=*)
        ENV="${1#*=}"
        shift
        ;;
        --host=*)
        HOST="${1#*=}"
        shift
        ;;
        --port=*)
        PORT="${1#*=}"
        shift
        ;;
        --no-debug)
        DEBUG="false"
        shift
        ;;
        *)
        echo "Unknown parameter: $1"
        exit 1
        ;;
    esac
done

# Export environment variables
export FLASK_ENV=$ENV
export FLASK_DEBUG=$DEBUG

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application
python run.py --host=$HOST --port=$PORT --debug=$DEBUG