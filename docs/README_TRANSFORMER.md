---
title: README for Transformer
---

# Amphitrite swell table transformation

This package sits under Amphitrite is designed pull the swell partition tables stored in the Amphitrite database and apply a transformation on the tables. Table output is used by Amphitrite on demand API as well as saved in `csv` format for ingesting to Vulture

## Features

-   Dashboard for configuration and interogation of the configs and the output.
-   Applies transformations based on user-defined parameters such as direction angles, multipliers, and attenuation.
-   Outputs modified transformed swell tables to html and csv, further used form ingesting to Vulture and Amphitrite.

## Algorithm

<div align="left">
    <img src="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/docs/transformer_algo.png" alt="Algorithm" width="80%"/>
</div>

## Usage

The transformer execution script sits under the root directory of the Amphitrite package

-   `run_transformer.py`

### Command Line Arguments

-   `--all`: If used, generate all sites output from config file (default: not used)
-   `--siteName`: The name of the site (default: "Dampier Salt - Cape Cuvier 7 days").
-   `--dir_land`: The average dirction towards the land (default: 90)
-   `--theta_1` Western angle for direction transformation (default: 262)
-   `--theta_2`: Eastern angle for direction transformation (default: 20)
-   `--multiplier`: Multiplier for the wave heights (default: 1.0).
-   `--attenuation`: Attenuation factor for the wave periods (default: 1.0).
-   `--thresholds`: 3 comma-separated threshold values for significant wave heights (default: "0.3,0.2,0.15").
-   `--run_time`: Optionally pass a run Time: YYYYMMDDHH (default: None)
-   `--notrans`: If used, Transformed=False (default: not used)
-   `--nosave`: If used, dont save the file to disk (default: not used)

### Running the Script

```bash
./run_transformer.py --siteName "Dampier Salt - Cape Cuvier" --tableName "Your_Table_Name" --dir_land 90 --theta_1 260 --theta_2 020 --multiplier 1.0 --attenuation 1.0 --thresholds "0.3,0.2,0.15"
```

To execute transformation of all configured sites

```bash
./run_transformer.py --all
```

## Configuration

Edit `transformer_configs.py` to set base directories or other global settings.

## Output

The script generates a CSV file with the transformed wave data in the specified output directory. It also prints an HTML table to the console for quick review. HTML output now going to the Gerling Hanson map for visulalisation

### File Descriptions

**api.cgi**:

-   CGI script for the API.

**save_transformer_config**:

-   Script to handle saving editied transform configuration data from the dashboard to a config text file that is used by the transformer.

**sites.py**:

-   Script to return active Ofcast sites.

**transform.py**:

-   Module that contains the main Transfrom class

**transformer_configs.py**:

-   Module used for site configuration paths

**transformer_site_configs.txt**:

-   Text file containing the config parameters

**html/**:

-   Dashboard php and config files

**docs/**:

-   Documentation kept here

## Author

Daz Vink: daz.vink@bom.gov.au
