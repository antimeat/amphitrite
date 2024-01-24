# CGI Script for Wave Data Partitioning retrieval from database

## Overview

This CGI script, provides a simple interface for managing and retrieving wave data. It offers functionalities like listing sites, fetching specific wave table data, and handling exclusion lists, both in HTML and JSON formats.

## Features

-   List all sites as links in an HTML table format.
-   Provide database checks and return results in HTML.
-   Return site configurations and exclusion lists in JSON format.
-   Fetch wave table data for specific sites and run times.

## Usage

The script can be accessed via HTTP requests with specific parameters:

### Endpoints

-   **List Sites (HTML)**: `GET http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=list_html`
-   **Database Check (HTML)**: `GET http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=database`
-   **List Sites (JSON)**: `GET http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=list_json`
-   **Exclusion List (JSON)**: `GET http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=exclusion`
-   **Site Wave Data (JSON)**: `GET http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=site&site_name=[SITE_NAME]&run_time=[RUN_TIME]`

### Examples

-   To list all sites as HTML: `http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=list_html`
-   To get JSON data for a specific site: `http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=site&site_name=Woodside%20-%20Pluto%207%20days`

## Logging

Errors are logged to `[LOG_FILE_PATH]`. Ensure the log file is writable by the web server.
