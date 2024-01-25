# Amphitrite

Amphitrite is designed for processing and partitioning wave spectrum data. Utilizing data from Auswave, with a view to incorporate SWAN model output, Amphitrite creates bespoke swell partitions based on specified period ranges.

## Features

-   **Dashboard**: GUI for maintaining configuration, monitoring logs and manual activation of scripts.
-   **Partition Splitting**: Splits wave spectrum data into specified swell partitions.
-   **Customizable Configurations**: Users can define their own partition ranges and site configurations.
-   **Automated Execution**: Configured to run automatically as a cron job for regular processing.
-   **Frontend API**: Provides an API endpoint for easy access to processed data.
-   **Backend Database**: Archives data for historical analysis and retrieval.

## Installation

Python package requirements are currently met on server `wa-vw-er` by using conda environment `mlenv`:

```bash
git clone git@gitlab.bom.gov.au:er/innovation/amphitrite.git
cd amphitrite
source activate mlenv
```

## Frontend Dashboard

Amphitrite features a user-friendly frontend dashboard for managing site configurations and manually activating the partition splitting scripts.

### Dashboard Features

-   **Site data**: API access to interogate current and recent data.
-   **Site Configuration**: Manage and update the configuration of various sites, including setting up partition ranges.
-   **Manual Script Activation**: Trigger the `partitionSplitter.py` script directly from the dashboard for immediate data processing.
-   **Logging**: Inspect log files

## API CGI Script

The `api.cgi` script in Amphitrite offers web-based functionalities to access and manage partitioned wave spectrum data. This CGI script, written in Python, allows users to interact through HTML and JSON formats.
A detailed guide for the `api.cgi` is here: [README](https://gitlab.bom.gov.au/er/innovation/amphitrite/-/blob/master/README_API.md)

## SITES_API CGI Script

A `sites_api.cgi` script is available for managing and visualizing wave data partitions and comparing output to Ofcast active sites. It provides various functionalities, such as comparing active sites with configuration files, listing sites in HTML or JSON formats, and handling site-specific data.
A detailed guide for the `sites_api.cgi` is here: [README](https://gitlab.bom.gov.au/er/innovation/amphitrite/-/blob/master/README_SITES_API.md)

## Backend usage

### Script: partitionSplitter.py

This script is the core of the Amphitrite package. It includes a `PartitionSplitter` class with methods to handle wave spectra data, transform it into different formats, and integrate it with a database.

### Running the Script

You can run the script manually or set it up to execute automatically using a cron job.

Manual execution:

```bash
python partitionSplitter.py --site [site_name|all]
```

### Automated Execution with Cron Job:

Currently run under user `davink` on server: `wa-vw-er`
The script is set up to run twice daily at 5:30 AM and 5:30 PM WST, ensuring regular data processing. As of `25/01/2024` Auswave data files have been arriving at approximately 5:20 AM and 5:20 PM WST.

```bash
30 5,17 * * * cd /cws/op/webapps/er_ml_projects/davink/amphitrite && /cws/anaconda/envs/mlenv/bin/python /cws/op/webapps/er_ml_projects/davink/amphitrite/partitionSplitter.py
```

## Logging

Errors are logged to `[cws/op/webapps/er_ml_projects/davink/amphitrite/api.log]`. Ensure the log file is writable by the web server.

## Author

Daz Vink: <daz.vink@bom.gov.au>
