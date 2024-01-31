---
title: Amphitrite
---

Amphitrite is designed for processing and partitioning wave spectrum data. Utilizing data from Auswave, with a view to incorporate SWAN model output in the future. Amphitrite creates bespoke swell partitions based on specified period ranges.

## Features

---

-   **Dashboard**: GUI for maintaining configuration, monitoring logs and manual activation of scripts (see <a href="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/html/dashboard.php" target="_blank">dashboard</a>).
-   **Partition Splitting**: Splits wave spectrum data into specified swell partitions.
-   **Customizable Configurations**: Users can define their own partition ranges and site configurations.
-   **Automated Execution**: Configured to run automatically as a cron job for regular processing.
-   **Frontend API**: Provides an API endpoint for easy access to processed data.
-   **Backend Database**: Archives data for past 7 days of model runs.

## Trouble shooting

---

1. [check the log](#logging)
2. [run manually from dashboard](#running-the-script-from-the-dashboard)
3. [check auswave files](#auswave-files)
4. [run manually from terminal](#running-the-script-manually)

## Frontend Dashboard

---

Amphitrite features a frontend <a href="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/html/dashboard.php" target="_blank">dashboard</a> for managing site configurations and manually activating the partition splitting scripts.

### Dashboard Features

-   **Site data**: API access to interogate current and recent data.
-   **Site Configuration**: Manage and update the configuration of various sites, including setting up partition ranges.
-   **Manual Script Activation**: Trigger the `partitionSplitter.py` script directly from the dashboard for immediate data processing.
-   **Logging**: Inspect log files

### Autoseas

API and package for calculating and returning autoseas swell data from winds and partitioned data. More detailed information is here (see <a href="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/docs/README_JSONAUTOSEAS.html" target="_blank">README_JSONAUTOSEAS</a>).

## Backend details

---

### File Descriptions

**api.cgi**:

-   CGI script for the API. More details in the [API](#api).

**autoseas/**:

-   A package for calculating and returning swell data from winds and partitioned data. Interfaces through `jsonAutoSeas.cgi`. Further details are in the [AutoSeas section](#autoseas).

**database.py**:

-   Provides backend database functions and interface.

**data.py**:

-   Utility functions for managing data.

**docs/**:

-   Home of the README documentation and script/css for rendering to html

**gfe.py**:

-   A function to retrieve point data from GFE.

**html/**:

-   Contains the frontend dashboard for the package. More details can be found in the [Frontend Dashboard section](#frontend-dashboard).

**jsonAutoSeas.cgi**:

-   CGI script for the AutoSeas interface. See [AutoSeas section](#autoseas) for more information.

**models.py**:

-   Contains descriptions of the database models.

**partition.py**:

-   A class for managing wave partitions and format.

**partitionSplitter.py**:

-   This is the main script that calls other partitioning scripts. It includes a `PartitionSplitter` class with methods to handle wave spectra data, transform it into different formats, and integrate/interact with the database.

    ### Running the script from the dashboard

    <a href="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/html/dashboard.php" target="_blank">go-to dashboard</a> -> Activate run

    ### Running the script manually

    You can run the script manually (it is automatically scheduled to run using a cron job).

    Manual execution:

    ```bash
    ssh wa-vw-er
    cd /cws/op/webapps/er_ml_projects/davink/amphitrite
    source activate mlenv
    python partitionSplitter.py --site [site_name|all]
    ```

**partition_smusher.py**:

-   A class designed to combine spectral data with AutoSeas data.

**readSpectrum.py**:

-   Backend script for partitioning wave spectra files.

**save_config.py**:

-   Used to update file `table_config.txt` and save to database (configuration file used for swell partitioning)

**save_exclusions.py**:

-   Used by [API](#api) and [dashboard](#frontend-dashboard) to configure the active sites to exclude from swell partitioning checks

**sites.py**:

-   Used by [API](#api) to get the current active sites.

**sites_api.cgi**:

-   Manages site-specific API interactions. See [Sites API](#sites-api) for more information.

**table_config.txt**:

-   The config file used by [API](#api) and [dashboard](#frontend-dashboard) for swell partitioning

**update_sites.py**:

-   Utility functions for initializing or updating the database. Used by save_config.py

**watchdog.sh**:

-   A shell script for monitoring the last run time of the cron job. Refer to [Cron section](#cron) for more details.

**waves_data.db**:

-   sqlite3 database used for storing the wave partitioned data (for up to 7 days).

### Cron:

Currently run under user `davink` on server: `wa-vw-er`
The script is set up to run every 3 minutes for 2 hours staring at 5:00AM, 9:00AM, 5:30PM and 9:00PM WST. A lock file (`.lockfile.lock`) and log file (`script_errors.log`) are used for checking if the script is already running and logging errors respectively. This should ensure regular/consistent data processing to begin within 5 minutes of data arriving. As of `25/01/2024` Auswave data files have been arriving at approximately 5:20AM, 9:20AM, 5:20PM and 9:20PM WST.

```bash
###########################
#scripts to run wave partitioning. check for new models every 3 minutes over a 2 hour period
###########################
*/3 5-6 * * * cd /cws/op/webapps/er_ml_projects/davink/amphitrite && /cws/op/webapps/er_ml_projects/davink/amphitrite/watchdog.sh
*/3 9-10 * * * cd /cws/op/webapps/er_ml_projects/davink/amphitrite && /cws/op/webapps/er_ml_projects/davink/amphitrite/watchdog.sh
*/3 17-18 * * * cd /cws/op/webapps/er_ml_projects/davink/amphitrite && /cws/op/webapps/er_ml_projects/davink/amphitrite/watchdog.sh
*/3 9-10 * * * cd /cws/op/webapps/er_ml_projects/davink/amphitrite && /cws/op/webapps/er_ml_projects/davink/amphitrite/watchdog.sh
############################
```

### Auswave files

The partition splitter relies on the timely arrival of the Auswave data files and a cron job to start the paritioning process (see [cron](#cron) for more details). The Auswave files arrive on server `wa-vw-er` here: `/cws/data/wavewatch/`.

```bash
ssh wa-vw-er
cd /cws/data/wavewatch/
ls -la
```

```
drwxr-xr-x.  2 cwsop cwsop      4096 Jan 25 09:20 .
drwxr-xr-x. 18 cwsop cwsop      4096 Jul 25  2023 ..
-rw-rw-r--.  1 cwsop cwsop  52309922 Jan 18 10:50 IDY35050_G3_2024011718.nc
-rw-rw-r--.  1 cwsop cwsop 165489628 Jan 18 17:20 IDY35050_G3_2024011800.nc
-rw-rw-r--.  1 cwsop cwsop  52298564 Jan 18 21:20 IDY35050_G3_2024011806.nc
-rw-rw-r--.  1 cwsop cwsop 165494747 Jan 19 05:20 IDY35050_G3_2024011812.nc
-rw-rw-r--.  1 cwsop cwsop  52294154 Jan 19 09:20 IDY35050_G3_2024011818.nc
```

## Api

---

The `api.cgi` script in Amphitrite offers web-based functionalities to access and manage partitioned wave spectrum data. This CGI script, written in Python, allows users to interact through HTML and JSON formats.
A detailed guide for the `api.cgi` is here: <a href="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/docs/README_API.html" target="_blank">README_API</a>

## Sites api

---

A `sites_api.cgi` script is available for managing and visualizing wave data partitions and comparing output to Ofcast active sites. It provides various functionalities, such as comparing active sites with configuration files, listing sites in HTML or JSON formats, and handling site-specific data.
A detailed guide for the `sites_api.cgi` is here: <a href="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/docs/README_SITES_API.html" target="_blank">README_SITES_API</a>

## Installation

---

Python package requirements are currently met on server `wa-vw-er` by using conda environment `mlenv`:

```bash
git clone git@gitlab.bom.gov.au:er/innovation/amphitrite.git
cd amphitrite
source activate mlenv
```

## Logging

---

Errors are logged to [logfile.log](http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/logfile.log). Ensure the log file is writable by the web server.

## Author

---

Daz Vink: <daz.vink@bom.gov.au>
