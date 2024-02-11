---
title: GET Winds API Documentation
---

## Overview

The `get_winds.cgi` script is designed to retrieve forecast wind data for a specified site, utilizing archived data to calculate and provide wind conditions in a structured JSON format. This document outlines the usage, request parameters, and response format for interacting with the GET Winds API.

## API Endpoint

-   **URL**: `http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/get_winds.cgi`

## Request Parameters

To fetch wind data, the following parameters must be provided in the request:

1. **`sessionID`** (optional):

    - Description: User session ID to authenticate requests.
    - Default: "davink46641"

2. **`fName`** (required):

    - Description: The forecast name identifying the specific site's wind data.
    - Example: "Woodside - Mermaid Sound 7 days"

3. **`archive`** (optional):

    - Description: The number of previous issues to retrieve (0 for current).
    - Default: 0

4. **`data_type`** (optional):
    - Description: Specifies the type of data requested, either forecast data or model data contained in the form.
    - Default: "forecast"

## Response Format

The API responds with a JSON object containing an array of wind conditions. Each entry in the array represents wind direction (degrees), wind speed (knots), and the time difference between consecutive readings (hours), formatted as follows:

```json
[
    [wind_dir, wind_spd, time_diff],
]
```

## Example Usage

To retrieve wind data for "Woodside - Mermaid Sound 7 days":
curl "http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/get_winds.cgi?fName=Woodside%20-%20Mermaid%20Sound%207%20days"

## Response Example

```json
[
    [230, 6, 3],
    [270, 10, 3],
    [300, 11, 3]
]
```

## Error Handling

In case of an error (e.g., missing parameters, failed data retrieval), the API will respond with an appropriate error message in JSON format:

```json
{
    "error": "Error message detailing the issue"
}
```

## Security Notes

-   Ensure that the sessionID parameter is securely handled to prevent unauthorized access.
-   Validate and sanitize all input parameters to mitigate injection attacks.

## Author

-   Script developed by Daz Vink.
    For further assistance or inquiries, please contact daz.vink@bom.gov.au.
