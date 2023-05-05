# Create Learning Circle

HTTP METHOD

`POST`

`/api/v1/lc/circle/create/`

## Description

Join or request to join a learning circle

## Request Options

### Authorization

| Key | Value |
| --- | --- |
| Bearer Token | eyJhbGciOiJIUzI1NiIsInR5cCI |

### HEADER

| Key | Value | Description |
| --- | --- | --- |
| userId | | |

### BODY

| Key | Value | Description |
| --- | --- | --- |
| circle_id | | |
| circle_code | | |
| secret_key | | |

## Response Success

| Key | Value |
| --- | --- |
| hasError | false |
| statusCode | 200 |
| message | { "general": ["Joined Successfully"] } |
| response | {} |

# Joining/Request Learning Circle

HTTP METHOD

`POST`

`api/v1/lc/circle/join/`

## Description

Creating a learning circle

## Request Options

### Authorization

| Key | Value |
| --- | --- |
| Bearer Token | eyJhbGciOiJIUzI1NiIsInR5cCI |

### HEADER

| Key | Value | Description |
| --- | --- | --- |
| userId | | |

### BODY

| Key | Value | Description |
| --- | --- | --- |
| circle_id | | |
| circle_code | | |
| secret_key | | |

## Response Success

| Key | Value |
| --- | --- |
| hasError | false |
| statusCode | 200 |
| message | { "general": ["Joined Successfully"] } |
| response | {} |

### Success when secret_key is not provided

| Key | Value |
| --- | --- |
| hasError | false |
| statusCode | 200 |
| message | { "general": ["Requested Successfully"] } |
| response | {} |

# Accept User to Learning Circle

HTTP METHOD

`POST`

`/api/v1/lc/circle/accept/`

## Description

Creating a learning circle

## Request Options

### Authorization

| Key | Value |
| --- | --- |
| Bearer Token | eyJhbGciOiJIUzI1NiIsInR5cCI |

### HEADER

| Key | Value | Description |
| --- | --- | --- |
| circle_id | | |

### BODY

| Key | Value | Description |
| --- | --- | --- |
|  |  |  |

## Response Success

| Key | Value |
| --- | --- |
| hasError | false |
| statusCode | 200 |
| message | ["Accepted Successfully"] |
| response | {} |
