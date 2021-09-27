# Commands

### To start

```bash
docker compose up
```

### Populate db

```bash
python setup_case.py create-objects --user 10
```

```bash
python setup_case.py create-objects --book 100000
```

### Test celery worker

```bash
python setup_case.py celery-test --celery 100000 --user_id 6150ddb8fbac96018969a736
```
