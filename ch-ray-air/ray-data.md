# Ray Data
:label:`ray-data`

```{.python .input}
# Hide code
# Hide outputs
import ray

if ray.is_initialized:
    ray.shutdown()

ray.init()
```

```{.python .input}
dataset = ray.data.read_parquet(
    "s3://anyscale-training-data/intro-to-ray-air/nyc_taxi_2021.parquet"
)
```

