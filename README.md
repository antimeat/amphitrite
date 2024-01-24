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

Provide instructions on how to install Amphitrite. This might include steps to clone a repository, install dependencies, or set up a virtual environment. For example:

```bash
git clone https://github.com/yourusername/amphitrite.git
cd amphitrite
pip install -r requirements.txt
```

## Frontend Dashboard

Amphitrite features a user-friendly frontend dashboard for managing site configurations and manually activating the partition splitting scripts.

### Dashboard Features

-   **Site Configuration**: Manage and update the configuration of various sites, including setting up partition ranges.
-   **Manual Script Activation**: Trigger the `partitionSplitter.py` script directly from the dashboard for immediate data processing.

## API CGI Script

The `api.cgi` script in Amphitrite offers web-based functionalities to access and manage partitioned wave spectrum data. This CGI script, written in Python, allows users to interact through HTML and JSON formats.

### Features

-   **HTML and JSON Responses**: Outputs data in HTML for web presentation and JSON for programmatic access.
-   **Site Listing**: Lists sites and associated data in both HTML and JSON formats.
-   **Database Interactions**: Fetches and displays data about sites, run times, and partitions from the database.
-   **Configuration File Processing**: Processes configuration files into structured JSON data.
-   **Customizable HTML Rendering**: Includes custom CSS styles for rendering HTML tables.

### Endpoints and Parameters

-   `/api.cgi?get=list_html` - Lists all sites as HTML links.
-   `/api.cgi?get=database` - Displays database entries in HTML format.
-   `/api.cgi?get=list_json` - Lists all sites and data in JSON format.
-   `/api.cgi?get=exclusion` - Lists exclusion sites in JSON format.
-   `/api.cgi?get=site&site_name=[name]&run_time=[time]` - Fetches data for a specific site and run time.

### Examples

-   **List Sites in HTML**:
    `url http://[base-url]/api.cgi?get=list_html`
-   **Get Specific Site Data in JSON**:
    `url http://[base-url]/api.cgi?get=site&site_name=ExampleSite&run_time=2024-01-01`

## Backend usage

### Script: partitionSplitter.py

This script is the core of the Amphitrite package. It includes a `PartitionSplitter` class with methods to handle wave spectra data, transform it into different formats, and integrate it with a database.

### Running the Script

You can run the script manually or set it up to execute automatically using a cron job.

Manual execution:

```bash
python partitionSplitter.py --site [site_name|all]
```

Automated Execution with Cron Job:
The script is set up to run twice daily at 5:30 AM and 5:30 PM, ensuring regular data processing.

```bash
30 5,17 * * * cd /cws/op/webapps/er_ml_projects/davink/amphitrite && /cws/anaconda/envs/mlenv/bin/python /cws/op/webapps/er_ml_projects/davink/amphitrite/partitionSplitter.py
```

## Contributing

Daz Vink: daz.vink@bom.gov.au
Leo Peach: leo.peach@bom.gov.au

## Contact

Daz Vink
