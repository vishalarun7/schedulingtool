# vishal take-home

you don't require anything but python3 to run the code. I've included a bunch of test cases in /tests to cover edge behaviour.

## Run

```bash
python3 render-schedule.py \
  --schedule=schedule.json \
  --overrides=overrides.json \
  --from='2026-11-06T17:00:00Z' \
  --until='2026-11-20T17:00:00Z'
```

## Test

```bash
bash tests/run_tests.sh
```
