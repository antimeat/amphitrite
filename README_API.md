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

### Endpoints and Parameters

-   `?get=list_html` - Lists all sites as HTML links.
-   `?get=database` - Displays database entries in HTML format.
-   `?get=list_json` - Lists all sites and data in JSON format.
-   `?get=exclusion` - Lists exclusion sites in JSON format.
-   `?get=site&site_name=[name]&run_time=[time]` - Fetches data for a specific site and run time.

### Examples

-   **List all sites in HTML**:
    `url http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=list_html`

    #### returns:

    |         Forecast site         | Auswave table |         Partitions          |
    | :---------------------------: | :-----------: | :-------------------------: |
    |        BHP - Pyrenees         |   Pyrenees    |  [0.001, 9.0], [9.0, 40.0]  |
    |   Boskalis - Dampier 7 Days   |  Dampier_Po   |  [0.001, 9.0], [9.0, 40.0]  |
    | Boskalis - Scarborough 7 Days |   Scarb_new   |  [0.001, 9.0], [9.0, 40.0]  |
    |       Chevron - Gorgon        |    Gorgon     | [0.001, 10.0], [10.0, 40.0] |
    |              ...              |      ...      |             ...             |

-   **List entries in database**:
    `url http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=database`

    #### returns:

    |             sites             |   table    |         partitions          | run_times  |
    | :---------------------------: | :--------: | :-------------------------: | :--------: |
    |        BHP - Pyrenees         |  Pyrenees  |  [0.001, 9.0], [9.0, 40.0]  | 24/0124/12 |
    |   Boskalis - Dampier 7 Days   | Dampier_Po |  [0.001, 9.0], [9.0, 40.0]  | 24/0124/00 |
    | Boskalis - Scarborough 7 Days | Scarb_new  |  [0.001, 9.0], [9.0, 40.0]  | 24/0123/12 |
    |       Chevron - Gorgon        |   Gorgon   | [0.001, 10.0], [10.0, 40.0] | 24/0123/00 |
    |              ...              |    ...     |             ...             |    ...     |

-   **List sites in json**:
    `url http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=list_json`

    #### returns:

    ```
    {
        "BHP - Pyrenees": {
            "table": "Pyrenees",
            "parts": [
                [
                    0.001,
                    9
                ],
                [
                    9,
                    40
                ]
            ]
        },
        ...,
        "Woodside - Dampier Port DPS1 10 days": {
            "table": "Dampier_Po",
            "parts": [
                [
                    0.001,
                    9
                ],
                [
                    9,
                    40
                ]
            ]
        }
    }
    ```

-   **List exclusion sites in json**:
    `url http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=exclusion`

    #### returns:

    ```
    {
        "Anglogold - Tropicana": {
            "name": "Anglogold - Tropicana"
        },
        "Santos - Van Gogh 4 days": {
            "name": "Santos - Van Gogh 4 days"
        },
        "Woodside - Logistics Learmonth 7 days": {
            "name": "Woodside - Logistics Learmonth 7 days"
        },
        "Chevron - Wheatstone Platform AFS": {
            "name": "Chevron - Wheatstone Platform AFS"
        },
        "Chevron Barrow Island AFS ML ext": {
            "name": "Chevron Barrow Island AFS ML ext"
        },
        "Woodside - Logistics Karratha 7 days": {
            "name": "Woodside - Logistics Karratha 7 days"
        },
        "Chevron - North Whites Beach": {
            "name": "Chevron - North Whites Beach"
        }
    }
    ```

-   **Get Specific Site Data in JSON**:
    `url http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=site&site_name=Woodside - Scarborough 10 Days&run_time=2024010112`

    #### returns

    ```
    ### AUSWAVE Partition Forecast ###
    # Location:  Woodside - Scarborough 10 Days
    # Table:  Scarb_new
    # StartTime: 1706097600
    # StartUTC:  20240124 1200
    # Partitions:  [0.001, 9.0], [9.0, 40.0]
    # Fields:    time[hrs], time[UTC], time[WST], wind_dir[degrees], wind_spd[kn], seasw_ht[m], seasw_dir[degree], seasw_pd[s], sea_ht[m], sea_dir[degree], sea_pd[s], sw1_ht[m], sw1_dir[degree], sw1_pd[s]
    ###
    000,  2024-01-24 12:00,  2024-01-24 20:00,  201,  19,  3.02,  204,  9,   2.59,  204,  9,  1.55,  204,  17
    001,  2024-01-24 13:00,  2024-01-24 21:00,  203,  19,  2.97,  204,  9,   2.54,  204,  9,  1.53,  204,  17
    002,  2024-01-24 14:00,  2024-01-24 22:00,  204,  19,  2.93,  204,  9,   2.5,   204,  9,  1.52,  204,  17
    003,  2024-01-24 15:00,  2024-01-24 23:00,  206,  19,  2.89,  204,  9,   2.46,  204,  9,  1.5,   204,  17
    ```

## Logging

Errors are logged to `[cws/op/webapps/er_ml_projects/davink/amphitrite/api.log]`. Ensure the log file is writable by the web server.

## Author

Daz Vink: <daz.vink@bom.gov.au>
