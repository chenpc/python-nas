# Run Larva

    gunicorn --reload --preload -k sync -b 0.0.0.0:8080 -w 2 nas:app
