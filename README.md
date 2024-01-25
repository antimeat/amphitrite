# Amphitrite

Amphitrite is designed for processing and partitioning wave spectrum data. Utilizing data from Auswave, with a view to incorporate SWAN model output, Amphitrite creates bespoke swell partitions based on specified period ranges.

## Trouble shooting

1. [check the log](#logging)
2. [run manually from dashboard](#running-the-script-from-the-dashboard)
3. [check auswave files](#auswave-files)
4. [run manually from terminal](#running-the-script-manually)

## Features

-   **Dashboard**: GUI for maintaining configuration, monitoring logs and manual activation of scripts.
-   **Partition Splitting**: Splits wave spectrum data into specified swell partitions.
-   **Customizable Configurations**: Users can define their own partition ranges and site configurations.
-   **Automated Execution**: Configured to run automatically as a cron job for regular processing.
-   **Frontend API**: Provides an API endpoint for easy access to processed data.
-   **Backend Database**: Archives data for past 7 days of model runs.

## Frontend Dashboard

Amphitrite features a frontend [dashboard](http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/html/dashboard.php) for managing site configurations and manually activating the partition splitting scripts.

### Dashboard Features

-   **Site data**: API access to interogate current and recent data.
-   **Site Configuration**: Manage and update the configuration of various sites, including setting up partition ranges.
-   **Manual Script Activation**: Trigger the `partitionSplitter.py` script directly from the dashboard for immediate data processing.
-   **Logging**: Inspect log files

## Backend details

### Script: partitionSplitter.py

This is the main script that calls other partitioning scripts. It includes a `PartitionSplitter` class with methods to handle wave spectra data, transform it into different formats, and integrate/interact with the database.

### Running the script from the dashboard

[go-to dashboard](http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/html/dashboard.php)
-> Activate run

### Running the script manually

You can run the script manually (it is automatically scheduled run using a cron job).

Manual execution:

```bash
ssh wa-vw-er
cd /cws/op/webapps/er_ml_projects/davink/amphitrite
source activate mlenv
python partitionSplitter.py --site [site_name|all]
```

### Cron:

Currently run under user `davink` on server: `wa-vw-er`
The script is set up to run twice daily at 5:30 AM and 5:30 PM WST, ensuring regular data processing. As of `25/01/2024` Auswave data files have been arriving at approximately 5:20 AM and 5:20 PM WST.

```bash
30 5,17 * * * cd /cws/op/webapps/er_ml_projects/davink/amphitrite && /cws/anaconda/envs/mlenv/bin/python /cws/op/webapps/er_ml_projects/davink/amphitrite/partitionSplitter.py
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

## api script

The `api.cgi` script in Amphitrite offers web-based functionalities to access and manage partitioned wave spectrum data. This CGI script, written in Python, allows users to interact through HTML and JSON formats.
A detailed guide for the `api.cgi` is here: [README_API](https://gitlab.bom.gov.au/er/innovation/amphitrite/-/blob/master/README_API.md)

## sites_api script

A `sites_api.cgi` script is available for managing and visualizing wave data partitions and comparing output to Ofcast active sites. It provides various functionalities, such as comparing active sites with configuration files, listing sites in HTML or JSON formats, and handling site-specific data.
A detailed guide for the `sites_api.cgi` is here: [README_SITES_API](https://gitlab.bom.gov.au/er/innovation/amphitrite/-/blob/master/README_SITES_API.md)

## Installation

Python package requirements are currently met on server `wa-vw-er` by using conda environment `mlenv`:

```bash
git clone git@gitlab.bom.gov.au:er/innovation/amphitrite.git
cd amphitrite
source activate mlenv
```

## Logging

Errors are logged to [logfile.log](http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/logfile.log). Ensure the log file is writable by the web server.

## Author

Daz Vink: <daz.vink@bom.gov.au>
