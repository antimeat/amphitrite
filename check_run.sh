#!/bin/bash

# Paths to your directories and files
SCRIPT_DIR="/cws/op/webapps/er_ml_projects/davink/amphitrite"
LOG_FILE="$SCRIPT_DIR/script_errors.log"
LAST_RUN_FILE="$SCRIPT_DIR/.last_check"
EMAIL_SCRIPT="$SCRIPT_DIR/emails.py"

# Maximum interval in seconds (3600 seconds = 1 hour)
MAX_INTERVAL=3600

# Current time in seconds since the epoch
current_time=$(date +%s)

cd "$SCRIPT_DIR/" || { echo "$(date) - Failed to change directory to $SCRIPT_DIR." >> "$LOG_FILE"; exit 1; }

# Check if the last run file exists
if [ -f "$LAST_RUN_FILE" ]; then
    last_run_time=$(date -r "$LAST_RUN_FILE" +%s)
    interval=$((current_time - last_run_time))

    if [ $interval -gt $MAX_INTERVAL ]; then
        echo "$(date) - The script has not run in the last hour." >> "$LOG_FILE"
        # Call the email script to send a failure notification
        "$EMAIL_SCRIPT" --fail --message "Amphitrite has not run in the past hour" 2>> "$LOG_FILE"
    fi
else
    echo "$(date) - The last run file does not exist. Creating file..." >> "$LOG_FILE"
    touch "$LAST_RUN_FILE"  # Create the file to prevent future false alerts
fi
