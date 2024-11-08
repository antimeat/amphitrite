---
title: API for Autoseas, partitioned seas and smushed seas
---

## Overview

---

The autoseas API provides sea state based on wind conditions at a given site. In the backend there are fetch and depth tables for each site that need to be maintained. Fetch and depth tables are used as part of the Autoseas generated seas calculations

## API Endpoint

---

-   **URL**: `http://wa-vw-er/webapps/amphitrite/autoseas.cgi`

## Request Parameters

The API accepts the following query parameters:

1. `first_time_step` (required)

    - Format: `YYYYMMDDHH`
    - Description: Indicates the time step of the first wind values in UTC.

2. `site` (required)

    - Format: String with `%20` as whitespace
    - Description: Specifies the site name for partitioned data retrieval.

3. `src` (required)

    - Values: `autoseas`, `smush`, `partition`
    - `autoseas`: Auto seas calculation based on the winds passed
    - `smush`: A smush of the Auswave partitioned data and the autoseas generated winds. Highest energy at each timestep wins.
    - `partition`: Auswave swell partitioned data

4. `winds` (required)
    - Format: `dir[degrees]/spd[kts]/time_period[hrs]`
    - Description: Specifies winds to use for calculations depending on `src` parameter. Format is direction (degrees), speed (knots), and time period (hours). Time period is the time difference between the last wind and the current.

## Response Format

The response is a JSON object with the following structure:
{"seas": [[seas_hs, seas_pd, seas_dir]]}

-   `seas_hs`: Sea state height (meters).
-   `seas_pd`: Period of the sea state (hours).
-   `seas_dir`: Direction of the sea state (degrees).
-   Note: if zero value wind speed and direction are passed; eg: `0/0/3`, we assume the direction is `360` and default to a speed of `0.1` kts, to avoid divide by zero problems in seas calculations. Thus returning {"seas": [[`0.1, 0, 360`]]}

## Example

---

**get autoseas**

`url http://wa-vw-er/webapps/amphitrite/autoseas.cgi?first_time_step=2024012212&site=Woodside%20-%20Scarborough%2010%20Days&src=autoseas&winds=200/10/3,210/20/3,220/30/3`

## returns

{"seas": [[0.4, 4, 200], [0.8, 6, 210], [1.7, 6, 220]]}

## Author

---

Daz Vink: daz.vink@bom.gov.au
