---
title: README for Transformer
---

# Wave Transformation Package

This Python package is designed to scrape, transform, and save wave data tables for specified locations and conditions. It leverages BeautifulSoup for web scraping and pandas for data manipulation.

## Features

-   Scrapes wave data tables from specified URLs.
-   Applies transformations based on user-defined parameters such as direction angles, multipliers, and attenuation.
-   Calculates significant wave heights with customizable threshold settings.
-   Outputs modified wave data to CSV files for further analysis or reporting.

## Requirements

-   Python 3.x
-   BeautifulSoup4
-   pandas
-   numpy
-   urllib
-   ssl

## Usage

To use the WaveTable class and its functionalities, you can run the main script from the command line with optional arguments to customize the transformation process.

### Command Line Arguments

-   `--siteName`: The name of the site (default: "Dampier Salt - Cape Cuvier 7 days").
-   `--tableName`: The specific table to scrape from the site (default: "Cape_Cuvier_Offshore").
-   `--theta_1` Western angle for direction transformation
-   `--theta_2`: Eastern angle for direction transformation
-   `--multiplier`: Multiplier for the wave heights (default: 1.0).
-   `--attenuation`: Attenuation factor for the wave periods (default: 1.0).
-   `--model`: Model type for the data scraping, can be "long" or "short" (default: "long").
-   `--thresholds`: 3 comma-separated threshold values for significant wave heights (default: "0.3,0.2,0.15").

### Running the Script

```bash
./waveTable.py --siteName "Dampier Salt - Cape Cuvier" --tableName "Your_Table_Name" --theta_1 260 --theta_2 020 --multiplier 1.0 --attenuation 1.0 --model long --thresholds "0.3,0.2,0.15"
```

## Configuration

Edit `transformer_configs.py` to set base directories or other global settings.

## Output

The script generates a CSV file with the transformed wave data in the specified output directory. It also prints an HTML table to the console for quick review.

## Author

Daz Vink: daz.vink@bom.gov.au
