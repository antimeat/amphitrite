# CGI/API Script for Wave Data Partitioning

## Overview

CGI/API interface for managing and visualizing wave data site information. It provides various functionalities, such as comparing active sites with configuration files, listing sites in HTML or JSON formats, and handling site-specific data.

## Features

-   List wave data sites in both HTML and JSON formats.
-   Compare active sites with site configurations and exclusions.
-   Fetch and display site-specific data.
-   Handle active partition names and site titles with latitude and longitude information.

## Usage

The script supports various endpoints for different functionalities:

### Endpoints

-   **List Sites in HTML**: `GET http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi`
-   **List Sites in JSON**: `GET http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=json_sites`
-   **Compare Sites and Configuration**: `GET http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=compare`
-   **List Active Partition Names**: `GET http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=active_sites`

### Examples

-   To list all sites in HTML: `http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi`
-   To get JSON data for site titles: `http://wa-vw-er/cws/op/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=json_sites`

## Logging

Errors and important events are logged to the file specified in `LOG_FILE`. Ensure the web server has write access to this file for effective logging.
