---
title: Amphitrite swell table transformation
---

This package sits under Amphitrite. It retrieves the swell partition tables stored in the Amphitrite database and applies a transformation. Table output is used by Amphitrite on demand API. Output is also saved in `csv` format for ingesting to Vulture, and html format for view.

## Features

-   Dashboard for configuration and interogation of the configs and the output.
-   Applies transformations based on user-defined parameters for window angles, multiplier, and attenuation.
-   Outputs modified transformed swell tables to html and csv, further used for ingesting to Vulture and Amphitrite.

## Usage

The transformer execution script sits under the root directory of the Amphitrite package

-   `run_transformer.py`

### Command Line Arguments

-   `--all`: If used, generate all sites output from config file (default: not used)
-   `--siteName`: The name of the site (default: "Dampier Salt - Cape Cuvier 7 days").
-   `--theta_split`: The angle that splits theat_1 and theta_2 (default: 90)
-   `--theta_1` 1st angle for direction transformation (default: 262)
-   `--theta_2`: 2nd angle for direction transformation (default: 20)
-   `--multi_short`: Multiplier for short period wave heights (default: 1.0).
-   `--multi_long`: Multiplier for long period wave heights (default: 1.0).
-   `--attenuation`: Attenuation factor for the wave periods (default: 1.0).
-   `--thresholds`: 3 comma-separated threshold values for significant wave heights (default: "0.3,0.2,0.15").
-   `--run_time`: Optionally pass a run Time: YYYYMMDDHH (default: None)
-   `--notrans`: If used, Transformed=False (default: not used)
-   `--nosave`: If used, dont save the file to disk (default: not used)

### Running the Script

Run transformer on an indivual site

```bash
./run_transformer.py --siteName "Dampier Salt - Cape Cuvier" --theta_split 90 --theta_1 260 --theta_2 020 --multi_short 0.7 --multi_long 1.0 --attenuation 1.0 --thresholds "0.3,0.2,0.15"
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
