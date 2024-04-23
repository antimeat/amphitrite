#!/bin/bash

WATCH_DIR="/cws/data/wavewatch/"
SCRIPT_DIR="/cws/op/webapps/er_ml_projects/davink/amphitrite_dev/amphitrite"
LOG_FILE="$SCRIPT_DIR/script_errors.log"

LOCK_FILE="$SCRIPT_DIR/.lockfile.lock"
LAST_RUN_FILE="$SCRIPT_DIR/.last_check"
SCRIPT="partitionSplitter.py"
OUTPUT_SCRIPT="run_transform.py"

# Check if the lock file exists
if [ -f "$LOCK_FILE" ]; then
    echo "$(date) - Another instance of the script is running. Exiting." >> "$LOG_FILE"
    exit 1
fi

# Create a lock file
touch "$LOCK_FILE" 2>> "$LOG_FILE"

# Find new files since last run
new_files=$(find "$WATCH_DIR" -type f -newer "$LAST_RUN_FILE" 2>> "$LOG_FILE")

# Change directory to script directory and run your script if new files are found
if [[ ! -z "$new_files" ]]; then
    cd "$SCRIPT_DIR/" || { echo "$(date) - Failed to change directory to $SCRIPT_DIR." >> "$LOG_FILE"; exit 1; }
    echo "$(date) - Splitting has commenced." >> "$LOG_FILE"
    "./$SCRIPT" 2>> "$LOG_FILE"
    
    # Run the transformer output script
    echo "$(date) - Transforming output to csv and html has commenced." >> "$LOG_FILE"
    "./$OUTPUT_SCRIPT" --all 2>> "$LOG_FILE"
fi

# Update last run file timestamp for next run
touch "$LAST_RUN_FILE" 2>> "$LOG_FILE"

# Remove the lock file
rm "$LOCK_FILE" 2>> "$LOG_FILE"
