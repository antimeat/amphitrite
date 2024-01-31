---
title: API for sites, table and configuration data
---

## Overview

---

CGI/API interface for managing and visualizing wave data partitions and comparing output to Ofcast active sites. It provides various functionalities, such as comparing active sites with configuration files, listing sites in HTML or JSON formats, and handling site-specific data.

## Features

---

-   List wave data sites in both HTML and JSON formats.
-   Compare active sites with site configurations and exclusions.
-   Fetch and display site-specific data.
-   Handle active partition names and site titles with latitude and longitude information.

## API Endpoint

---

The API supports various endpoints, some with its own set of parameters.

## Request Parameters

1. `get=list_html` (default)

    - No additional parameters required.
    - Description: Lists all sites as HTML links.

2. `get=database`

    - No additional parameters required.
    - Description: Displays database entries in HTML format.

3. `get=list_json`

    - No additional parameters required.
    - Description: Lists all sites and data in JSON format.

4. `get=exclusion`

    - No additional parameters required.
    - Description: Lists exclusion sites in JSON format.

5. `get=site`

    - `site_name` (required)
        - Format: String with `%20` as whitespace
        - Description: Specifies the site name for data retrieval.
    - `run_time` (required)
        - Format: `YYYYMMDDHH`
        - Description: Indicates the time step for data retrieval in UTC.

Each endpoint serves a specific purpose and may require different parameters to function correctly. The `site_name` and `run_time` parameters are essential for fetching data related to a specific site and time.

### Examples

-   **List table names in HTML**:
    `url http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/sites_api.cgi`

    #### returns:

    |    name     |  lat   |   lon   |
    | :---------: | :----: | :-----: |
    | 22.5_107.5  | -22.5  |  107.5  |
    | Abbot_Poin  | -19.8  | 148.07  |
    |  Adelaide   | -34.75 | 138.375 |
    |     ...     |  ...   |   ...   |
    |   Wickham   | -12.52 | 130.84  |
    | Wonthaggi\_ | -38.59 | 145.51  |
    |    Xena     | -19.96 | 115.218 |
    |    Yoorn    | -20.34 | 115.79  |

-   **List table names in json**:
    `url http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/sites_api.cgi?get=json_tables`

    #### returns:

    ```
    [
        {
            "name": "22.5_107.5",
            "lat": -22.5,
            "lon": 107.5
        },
        {
            "name": "Abbot_Poin",
            "lat": -19.8,
            "lon": 148.07
        },
        ...,
        {
            "name": "Xena",
            "lat": -19.96,
            "lon": 115.218
        },
        {
            "name": "Yoorn",
            "lat": -20.34,
            "lon": 115.79
        }
    ]

    ```

-   **List active sites in HTML**:
    `url http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/sites_api.cgi?get=html_sites`

    #### returns:

    | Company   | Project Name        | Coordinates      |
    | --------- | ------------------- | ---------------- |
    | Anglogold | Tropicana           | -29.24, 124.54   |
    | Boskalis  | Dampier 7 Days      | -20.6, 116.75    |
    | Chevron   | Gorgon              | -20.46, 114.84   |
    | ...       | ...                 | ...              |
    | Woodside  | Pyrenees            | -21.54, 114.12   |
    | Woodside  | Scarborough 10 days | -19.926, 113.242 |
    | Woodside  | Stybarrow 10 Days   | -21.45, 113.82   |

-   **List all sites in HTML**:
    `url http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/sites_api.cgi?get=compare`

    #### returns:

            Active Sites

    |       Forecast site       |   lat    |   lon   |
    | :-----------------------: | :------: | :-----: |
    |   Anglogold - Tropicana   | -29.2400 | 124.540 |
    | Boskalis - Dampier 7 Days | -20.6000 | 116.750 |
    |     Chevron - Gorgon      | -20.4600 | 114.840 |
    |      Chevron - Jansz      | -19.8100 | 114.610 |
    |            ...            |   ...    |   ...   |

            Site Configurations

    |             site              |   table    |         partitions          |
    | :---------------------------: | :--------: | :-------------------------: |
    |        BHP - Pyrenees         |  Pyrenees  |  [0.001, 9.0], [9.0, 40.0]  |
    |   Boskalis - Dampier 7 Days   | Dampier_Po |  [0.001, 9.0], [9.0, 40.0]  |
    | Boskalis - Scarborough 7 Days | Scarb_new  |  [0.001, 9.0], [9.0, 40.0]  |
    |       Chevron - Gorgon        |   Gorgon   | [0.001, 10.0], [10.0, 40.0] |
    |              ...              |    ...     |             ...             |

            Active Sites Not excluded

    |              site              |
    | :----------------------------: |
    |        Santos - Barossa        |
    | Woodside - Scarborough 10 days |
    |     Santos - Barossa KP40      |

            Excluded from Active Sites

    |                 name                  |
    | :-----------------------------------: |
    |         Anglogold - Tropicana         |
    |     Chevron - North Whites Beach      |
    |   Chevron - Wheatstone Platform AFS   |
    |   Chevron Barrow Island AFS ML ext    |
    |       Santos - Van Gogh 4 days        |
    | Woodside - Logistics Karratha 7 days  |
    | Woodside - Logistics Learmonth 7 days |

## Logging

---

Errors are logged to <a href="http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/sites_api.log" target="_blank">sites_api.log</a>. Ensure the log file is writable by the web server.

## Author

---

Daz Vink: <daz.vink@bom.gov.au>
