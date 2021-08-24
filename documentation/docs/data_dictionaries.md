# Data Dictionaries

Data dictionaries should be created for each predictor and survey dataset. Dictionaries for the open-source data and Brazilian, Thai and Philippino survey data already exist and should be located in the data/meta/ folder. 

An exemplary data dictionary (for speedtest data) is shown below:

| Number      | Name      | Description                        | Type     | Binary     | Role         | Use     | Comment               |
| ----------- | ---------- | ----------------------------------- | ----------- | ----------- | --------------- | ----------- | ----------------------- |
| 1       | `avg_d_kbps` | The average download speed of all tests performed in the tile, represented in kilobits per second | num | N | predictor | Y | mbps can also be used |
| 2       | `avg_u_kbps` | The average upload speed of all tests performed in the tile, represented in kilobits per second | num | N | predictor | Y | mbps can also be used |
| 3       | `avg_lat_ms` | The average latency of all tests performed in the tile, represented in milliseconds | num | N | predictor | N | |
| 4       | `tests` | The number of tests taken in the tile | num | N | predictor | N | |
| 5       | `devices` | The number of unique devices contributing tests in the tile | num | N | predictor | N | |
