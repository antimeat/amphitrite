# jsonAutoSeas API Documentation

## Overview

The jsonAutoSeas API provides sea state predictions based on wind conditions. It's designed for marine and weather forecasting applications, integrating seamlessly into various analysis tools.

## API Endpoint

-   **URL**: `http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/jsonAutoSeas.cgi`

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
    - Description: Indicates the source of the sea state data.

4. `winds` (required)
    - Format: `dir[degrees]/spd[kts]/time_period[hrs]`
    - Description: Specifies wind conditions in direction (degrees), speed (knots), and time period (hours).

## Response Format

The response is a JSON object with the following structure:
{"seas": [[seas_hs, seas_pd, seas_dir]]}

-   `seas_hs`: Sea state height (meters).
-   `seas_pd`: Period of the sea state (hours).
-   `seas_dir`: Direction of the sea state (degrees).

## Example Request

http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/jsonAutoSeas.cgi?first_time_step=2024012212&site=Woodside%20-%20Scarborough%2010%20Days&src=autoseas&winds=200/10/3,210/20/3,220/30/3

## Example Response

{"seas": [[0.4, 4, 200], [0.8, 6, 210], [1.7, 6, 220]]}

## Usage

Provide guidelines on how to integrate or call this API in different environments or platforms.

## Error Handling

Describe common errors and their meanings, and how users should handle them.

## Versioning

Indicate the current version of the API and any previous versions if applicable.

## Contact

Provide contact information for users to report issues or seek support.

## License

Specify the license under which this API is released, if applicable.

---

Remember to update this document as your API evolves. It's crucial for maintaining clarity and ease of use for your API's consumers.
