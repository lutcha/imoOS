Apr 01 19:00:50 [migrate] [34m╭────────────[34m[30m[44m git repo clone [0m[0m[34m───────────╼[0m
Apr 01 19:00:50 [celery-beat] [34m╭────────────[34m[30m[44m git repo clone [0m[0m[34m───────────╼[0m
Apr 01 19:00:50 [celery-worker] [34m╭────────────[34m[30m[44m git repo clone [0m[0m[34m───────────╼[0m
Apr 01 19:00:50 [celery-worker] [34m│[0m [34m › fetching app source code[0m
Apr 01 19:00:50 [migrate] [34m│[0m [34m › fetching app source code[0m
Apr 01 19:00:50 [api] [34m╭────────────[34m[30m[44m git repo clone [0m[0m[34m───────────╼[0m
Apr 01 19:00:50 [celery-beat] [34m│[0m [34m › fetching app source code[0m
Apr 01 19:00:50 [celery-worker] [34m│[0m => Selecting branch "develop"
Apr 01 19:00:52 [celery-worker] [34m│[0m => Checking out commit "a13374d510b994aee17e40bbf035376512dbc0f0"
Apr 01 19:00:52 [celery-worker] [34m│[0m 
Apr 01 19:00:52 [celery-worker] [34m│[0m [32m ✔ cloned repo to [35m/.app_platform_workspace[0m[0m
Apr 01 19:00:52 [celery-worker] [34m╰────────────────────────────────────────╼[0m
Apr 01 19:00:52 [celery-worker] 
Apr 01 19:00:52 [celery-worker] [34m › configuring build-time app environment variables:[0m
Apr 01 19:00:52 [celery-worker]      REDIS_URL DB_PASSWORD CELERY_RESULT_BACKEND DB_USER DB_PORT DJANGO_SETTINGS_MODULE SECRET_KEY DB_NAME CELERY_BROKER_URL DB_HOST
Apr 01 19:00:52 [celery-worker] [34m╭────────────[34m[30m[44m dockerfile build [0m[0m[34m───────────╼[0m
Apr 01 19:00:52 [celery-worker] [34m│[0m [34m › using dockerfile [35m/.app_platform_workspace/docker/Dockerfile.staging[0m[0m
Apr 01 19:00:52 [celery-worker] [34m│[0m [34m › using build context [35m/.app_platform_workspace//[0m[0m
Apr 01 19:00:52 [celery-worker] [34m│[0m 
Apr 01 19:00:52 [celery-worker] [34m│[0m [36mINFO[0m[0000] Using dockerignore file: /.app_platform_workspace/.dockerignore 
Apr 01 19:00:52 [celery-worker] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:52 [celery-worker] [34m│[0m [36mINFO[0m[0000] Retrieving image library/python:3.11-slim-bookworm from registry mirror <registry-uri-0> 
Apr 01 19:00:50 [migrate] [34m│[0m => Selecting branch "develop"
Apr 01 19:00:50 [api] [34m│[0m [34m › fetching app source code[0m
Apr 01 19:00:50 [celery-beat] [34m│[0m => Selecting branch "develop"
Apr 01 19:00:53 [celery-worker] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:53 [celery-worker] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Built cross stage deps: map[]                
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Returning cached image manifest              
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Returning cached image manifest              
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Executing 0 build triggers                   
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Building stage 'python:3.11-slim-bookworm' [idx: '0', base-idx: '-1'] 
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Checking for cached layer <registry-uri-1> 
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Using caching version of cmd: RUN apt-get update && apt-get install -y     gdal-bin     libgdal-dev     libpq-dev     gcc     python3-pip     python3-cffi     python3-brotli     libpango-1.0-0     libpangocairo-1.0-0     libcairo2     libgdk-pixbuf-2.0-0     libffi-dev     shared-mime-info     && rm -rf /var/lib/apt/lists/* 
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Checking for cached layer <registry-uri-2> 
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Using caching version of cmd: RUN pip install --no-cache-dir -r requirements/production.txt 
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Checking for cached layer <registry-uri-3> 
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] No cached layer found for cmd RUN DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true 
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Cmd: EXPOSE                                  
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Adding exposed port: 8000/tcp                
Apr 01 19:00:51 [migrate] [34m│[0m => Checking out commit "a13374d510b994aee17e40bbf035376512dbc0f0"
Apr 01 19:00:50 [api] [34m│[0m => Selecting branch "develop"
Apr 01 19:00:50 [celery-beat] [34m│[0m => Checking out commit "a13374d510b994aee17e40bbf035376512dbc0f0"
Apr 01 19:00:54 [celery-worker] [34m│[0m [36mINFO[0m[0001] Unpacking rootfs as cmd COPY requirements/base.txt requirements/base.txt requires it. 
Apr 01 19:01:03 [celery-worker] [34m│[0m [36mINFO[0m[0010] Initializing snapshotter ...                 
Apr 01 19:01:03 [celery-worker] [34m│[0m [36mINFO[0m[0010] Taking snapshot of full filesystem...        
Apr 01 19:01:04 [celery-worker] [34m│[0m [36mINFO[0m[0011] RUN apt-get update && apt-get install -y     gdal-bin     libgdal-dev     libpq-dev     gcc     python3-pip     python3-cffi     python3-brotli     libpango-1.0-0     libpangocairo-1.0-0     libcairo2     libgdk-pixbuf-2.0-0     libffi-dev     shared-mime-info     && rm -rf /var/lib/apt/lists/* 
Apr 01 19:01:04 [celery-worker] [34m│[0m [36mINFO[0m[0011] Found cached layer, extracting to filesystem 
Apr 01 19:00:51 [migrate] [34m│[0m 
Apr 01 19:00:51 [migrate] [34m│[0m [32m ✔ cloned repo to [35m/.app_platform_workspace[0m[0m
Apr 01 19:00:51 [migrate] [34m╰────────────────────────────────────────╼[0m
Apr 01 19:00:51 [migrate] 
Apr 01 19:00:51 [migrate] [34m › configuring build-time app environment variables:[0m
Apr 01 19:00:51 [migrate]      DB_PORT APP_DOMAIN DJANGO_SETTINGS_MODULE SECRET_KEY TENANT_BASE_DOMAIN REDIS_URL DB_NAME DB_USER DB_HOST ALLOWED_HOSTS DB_PASSWORD
Apr 01 19:00:51 [migrate] [34m╭────────────[34m[30m[44m dockerfile build [0m[0m[34m───────────╼[0m
Apr 01 19:00:51 [migrate] [34m│[0m [34m › using dockerfile [35m/.app_platform_workspace/docker/Dockerfile.staging[0m[0m
Apr 01 19:00:51 [migrate] [34m│[0m [34m › using build context [35m/.app_platform_workspace//[0m[0m
Apr 01 19:00:51 [migrate] [34m│[0m 
Apr 01 19:00:51 [migrate] [34m│[0m [36mINFO[0m[0000] Using dockerignore file: /.app_platform_workspace/.dockerignore 
Apr 01 19:00:51 [migrate] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:51 [migrate] [34m│[0m [36mINFO[0m[0000] Retrieving image library/python:3.11-slim-bookworm from registry mirror <registry-uri-0> 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Built cross stage deps: map[]                
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Executing 0 build triggers                   
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Building stage 'python:3.11-slim-bookworm' [idx: '0', base-idx: '-1'] 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Checking for cached layer <registry-uri-1> 
Apr 01 19:00:51 [api] [34m│[0m => Checking out commit "a13374d510b994aee17e40bbf035376512dbc0f0"
Apr 01 19:00:50 [celery-beat] [34m│[0m 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Using caching version of cmd: RUN apt-get update && apt-get install -y     gdal-bin     libgdal-dev     libpq-dev     gcc     python3-pip     python3-cffi     python3-brotli     libpango-1.0-0     libpangocairo-1.0-0     libcairo2     libgdk-pixbuf-2.0-0     libffi-dev     shared-mime-info     && rm -rf /var/lib/apt/lists/* 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Checking for cached layer <registry-uri-2> 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Using caching version of cmd: RUN pip install --no-cache-dir -r requirements/production.txt 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Checking for cached layer <registry-uri-3> 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] No cached layer found for cmd RUN DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true 
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Cmd: EXPOSE                                  
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Adding exposed port: 8000/tcp                
Apr 01 19:00:52 [migrate] [34m│[0m [36mINFO[0m[0000] Unpacking rootfs as cmd COPY requirements/base.txt requirements/base.txt requires it. 
Apr 01 19:00:54 [migrate] [34m│[0m [36mINFO[0m[0002] Initializing snapshotter ...                 
Apr 01 19:00:54 [migrate] [34m│[0m [36mINFO[0m[0002] Taking snapshot of full filesystem...        
Apr 01 19:00:55 [migrate] [34m│[0m [36mINFO[0m[0003] RUN apt-get update && apt-get install -y     gdal-bin     libgdal-dev     libpq-dev     gcc     python3-pip     python3-cffi     python3-brotli     libpango-1.0-0     libpangocairo-1.0-0     libcairo2     libgdk-pixbuf-2.0-0     libffi-dev     shared-mime-info     && rm -rf /var/lib/apt/lists/* 
Apr 01 19:00:55 [migrate] [34m│[0m [36mINFO[0m[0003] Found cached layer, extracting to filesystem 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so 
Apr 01 19:00:51 [api] [34m│[0m 
Apr 01 19:00:50 [celery-beat] [34m│[0m [32m ✔ cloned repo to [35m/.app_platform_workspace[0m[0m
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] ENV PYTHONDONTWRITEBYTECODE=1                
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] ENV PYTHONUNBUFFERED=1                       
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] WORKDIR /app                                 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] Cmd: workdir                                 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] Changed working directory to /app            
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] Creating directory /app with uid -1 and gid -1 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] Taking snapshot of files...                  
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] COPY requirements/base.txt requirements/base.txt 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] Taking snapshot of files...                  
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] COPY requirements/production.txt requirements/production.txt 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] Taking snapshot of files...                  
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] RUN pip install --no-cache-dir -r requirements/production.txt 
Apr 01 19:01:52 [migrate] [34m│[0m [36mINFO[0m[0060] Found cached layer, extracting to filesystem 
Apr 01 19:00:51 [api] [34m│[0m [32m ✔ cloned repo to [35m/.app_platform_workspace[0m[0m
Apr 01 19:00:51 [api] [34m╰────────────────────────────────────────╼[0m
Apr 01 19:00:51 [api] 
Apr 01 19:00:52 [api] [34m › configuring build-time app environment variables:[0m
Apr 01 19:00:52 [api]      CELERY_RESULT_BACKEND APP_VERSION SECRET_KEY ALLOWED_HOSTS DB_USER AWS_ACCESS_KEY_ID AWS_S3_ENDPOINT_URL TENANT_BASE_DOMAIN CELERY_BROKER_URL AWS_SECRET_ACCESS_KEY DJANGO_SETTINGS_MODULE DB_PORT DB_HOST REDIS_URL SENTRY_DSN DEBUG AWS_STORAGE_BUCKET_NAME DB_NAME DB_PASSWORD
Apr 01 19:00:52 [api] [34m╭────────────[34m[30m[44m dockerfile build [0m[0m[34m───────────╼[0m
Apr 01 19:00:50 [celery-beat] [34m╰────────────────────────────────────────╼[0m
Apr 01 19:00:50 [celery-beat] 
Apr 01 19:00:50 [celery-beat] [34m › configuring build-time app environment variables:[0m
Apr 01 19:00:50 [celery-beat]      SECRET_KEY DB_NAME DB_USER DB_HOST REDIS_URL CELERY_RESULT_BACKEND CELERY_BROKER_URL DB_PASSWORD DJANGO_SETTINGS_MODULE DB_PORT
Apr 01 19:00:50 [celery-beat] [34m╭────────────[34m[30m[44m dockerfile build [0m[0m[34m───────────╼[0m
Apr 01 19:00:50 [celery-beat] [34m│[0m [34m › using dockerfile [35m/.app_platform_workspace/docker/Dockerfile.staging[0m[0m
Apr 01 19:00:50 [celery-beat] [34m│[0m [34m › using build context [35m/.app_platform_workspace//[0m[0m
Apr 01 19:00:50 [celery-beat] [34m│[0m 
Apr 01 19:00:50 [celery-beat] [34m│[0m [36mINFO[0m[0000] Using dockerignore file: /.app_platform_workspace/.dockerignore 
Apr 01 19:00:50 [celery-beat] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:50 [celery-beat] [34m│[0m [36mINFO[0m[0000] Retrieving image library/python:3.11-slim-bookworm from registry mirror <registry-uri-0> 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Built cross stage deps: map[]                
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Executing 0 build triggers                   
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Building stage 'python:3.11-slim-bookworm' [idx: '0', base-idx: '-1'] 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Checking for cached layer <registry-uri-1> 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Using caching version of cmd: RUN apt-get update && apt-get install -y     gdal-bin     libgdal-dev     libpq-dev     gcc     python3-pip     python3-cffi     python3-brotli     libpango-1.0-0     libpangocairo-1.0-0     libcairo2     libgdk-pixbuf-2.0-0     libffi-dev     shared-mime-info     && rm -rf /var/lib/apt/lists/* 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Checking for cached layer <registry-uri-2> 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Using caching version of cmd: RUN pip install --no-cache-dir -r requirements/production.txt 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Checking for cached layer <registry-uri-3> 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] No cached layer found for cmd RUN DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true 
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Cmd: EXPOSE                                  
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Adding exposed port: 8000/tcp                
Apr 01 19:00:51 [celery-beat] [34m│[0m [36mINFO[0m[0000] Unpacking rootfs as cmd COPY requirements/base.txt requirements/base.txt requires it. 
Apr 01 19:00:53 [celery-beat] [34m│[0m [36mINFO[0m[0002] Initializing snapshotter ...                 
Apr 01 19:00:53 [celery-beat] [34m│[0m [36mINFO[0m[0002] Taking snapshot of full filesystem...        
Apr 01 19:00:54 [celery-beat] [34m│[0m [36mINFO[0m[0003] RUN apt-get update && apt-get install -y     gdal-bin     libgdal-dev     libpq-dev     gcc     python3-pip     python3-cffi     python3-brotli     libpango-1.0-0     libpangocairo-1.0-0     libcairo2     libgdk-pixbuf-2.0-0     libffi-dev     shared-mime-info     && rm -rf /var/lib/apt/lists/* 
Apr 01 19:00:54 [celery-beat] [34m│[0m [36mINFO[0m[0003] Found cached layer, extracting to filesystem 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] ENV PYTHONDONTWRITEBYTECODE=1                
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] No files changed in this command, skipping snapshotting. 
Apr 01 19:00:52 [api] [34m│[0m [34m › using dockerfile [35m/.app_platform_workspace/docker/Dockerfile.staging[0m[0m
Apr 01 19:00:52 [api] [34m│[0m [34m › using build context [35m/.app_platform_workspace//[0m[0m
Apr 01 19:00:52 [api] [34m│[0m 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Using dockerignore file: /.app_platform_workspace/.dockerignore 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Retrieving image library/python:3.11-slim-bookworm from registry mirror <registry-uri-0> 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Built cross stage deps: map[]                
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Retrieving image manifest python:3.11-slim-bookworm 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Returning cached image manifest              
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Executing 0 build triggers                   
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Building stage 'python:3.11-slim-bookworm' [idx: '0', base-idx: '-1'] 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Checking for cached layer <registry-uri-1> 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Using caching version of cmd: RUN apt-get update && apt-get install -y     gdal-bin     libgdal-dev     libpq-dev     gcc     python3-pip     python3-cffi     python3-brotli     libpango-1.0-0     libpangocairo-1.0-0     libcairo2     libgdk-pixbuf-2.0-0     libffi-dev     shared-mime-info     && rm -rf /var/lib/apt/lists/* 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Checking for cached layer <registry-uri-2> 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Using caching version of cmd: RUN pip install --no-cache-dir -r requirements/production.txt 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Checking for cached layer <registry-uri-3> 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] No cached layer found for cmd RUN DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] ENV PYTHONUNBUFFERED=1                       
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] WORKDIR /app                                 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] Cmd: workdir                                 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] Changed working directory to /app            
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] Creating directory /app with uid -1 and gid -1 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] Taking snapshot of files...                  
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] COPY requirements/base.txt requirements/base.txt 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] Taking snapshot of files...                  
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] COPY requirements/production.txt requirements/production.txt 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] Taking snapshot of files...                  
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] RUN pip install --no-cache-dir -r requirements/production.txt 
Apr 01 19:01:53 [celery-beat] [34m│[0m [36mINFO[0m[0062] Found cached layer, extracting to filesystem 
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Cmd: EXPOSE                                  
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Adding exposed port: 8000/tcp                
Apr 01 19:00:52 [api] [34m│[0m [36mINFO[0m[0000] Unpacking rootfs as cmd COPY requirements/base.txt requirements/base.txt requires it. 
Apr 01 19:00:55 [api] [34m│[0m [36mINFO[0m[0002] Initializing snapshotter ...                 
Apr 01 19:00:55 [api] [34m│[0m [36mINFO[0m[0002] Taking snapshot of full filesystem...        
Apr 01 19:00:55 [api] [34m│[0m [36mINFO[0m[0003] RUN apt-get update && apt-get install -y     gdal-bin     libgdal-dev     libpq-dev     gcc     python3-pip     python3-cffi     python3-brotli     libpango-1.0-0     libpangocairo-1.0-0     libcairo2     libgdk-pixbuf-2.0-0     libffi-dev     shared-mime-info     && rm -rf /var/lib/apt/lists/* 
Apr 01 19:00:55 [api] [34m│[0m [36mINFO[0m[0003] Found cached layer, extracting to filesystem 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] ENV PYTHONDONTWRITEBYTECODE=1                
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] ENV PYTHONUNBUFFERED=1                       
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] No files changed in this command, skipping snapshotting. 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] WORKDIR /app                                 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] Cmd: workdir                                 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] Changed working directory to /app            
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] Creating directory /app with uid -1 and gid -1 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] Taking snapshot of files...                  
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] COPY requirements/base.txt requirements/base.txt 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] Taking snapshot of files...                  
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] COPY requirements/production.txt requirements/production.txt 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] Taking snapshot of files...                  
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] RUN pip install --no-cache-dir -r requirements/production.txt 
Apr 01 19:01:51 [api] [34m│[0m [36mINFO[0m[0059] Found cached layer, extracting to filesystem 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] No files changed in this command, skipping snapshotting. 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] No files changed in this command, skipping snapshotting. 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] ENV PYTHONDONTWRITEBYTECODE=1                
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] No files changed in this command, skipping snapshotting. 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] ENV PYTHONUNBUFFERED=1                       
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] No files changed in this command, skipping snapshotting. 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] WORKDIR /app                                 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] Cmd: workdir                                 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] Changed working directory to /app            
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] Creating directory /app with uid -1 and gid -1 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] Taking snapshot of files...                  
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] COPY requirements/base.txt requirements/base.txt 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] Taking snapshot of files...                  
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] COPY requirements/production.txt requirements/production.txt 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] Taking snapshot of files...                  
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] RUN pip install --no-cache-dir -r requirements/production.txt 
Apr 01 19:02:00 [celery-worker] [34m│[0m [36mINFO[0m[0067] Found cached layer, extracting to filesystem 
Apr 01 19:02:10 [migrate] [34m│[0m [36mINFO[0m[0078] COPY . .                                     
Apr 01 19:02:10 [migrate] [34m│[0m [36mINFO[0m[0078] Taking snapshot of files...                  
Apr 01 19:02:10 [api] [34m│[0m [36mINFO[0m[0078] COPY . .                                     
Apr 01 19:02:10 [api] [34m│[0m [36mINFO[0m[0078] Taking snapshot of files...                  
Apr 01 19:02:10 [migrate] [34m│[0m [36mINFO[0m[0078] RUN DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true 
Apr 01 19:02:11 [api] [34m│[0m [36mINFO[0m[0079] RUN DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true 
Apr 01 19:02:11 [migrate] [34m│[0m [36mINFO[0m[0079] Cmd: /bin/sh                                 
Apr 01 19:02:11 [migrate] [34m│[0m [36mINFO[0m[0079] Args: [-c DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true] 
Apr 01 19:02:11 [migrate] [34m│[0m [36mINFO[0m[0079] Running: [/bin/sh -c DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true] 
Apr 01 19:02:11 [celery-beat] [34m│[0m [36mINFO[0m[0080] COPY . .                                     
Apr 01 19:02:11 [celery-beat] [34m│[0m [36mINFO[0m[0080] Taking snapshot of files...                  
Apr 01 19:02:11 [api] [34m│[0m [36mINFO[0m[0079] Cmd: /bin/sh                                 
Apr 01 19:02:11 [api] [34m│[0m [36mINFO[0m[0079] Args: [-c DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true] 
Apr 01 19:02:11 [api] [34m│[0m [36mINFO[0m[0079] Running: [/bin/sh -c DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true] 
Apr 01 19:02:12 [celery-beat] [34m│[0m [36mINFO[0m[0081] RUN DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true 
Apr 01 19:02:12 [api] [34m│[0m 
Apr 01 19:02:12 [api] [34m│[0m 168 static files copied to '/app/staticfiles', 168 post-processed.
Apr 01 19:02:12 [migrate] [34m│[0m 
Apr 01 19:02:12 [migrate] [34m│[0m 168 static files copied to '/app/staticfiles', 168 post-processed.
Apr 01 19:02:13 [celery-beat] [34m│[0m [36mINFO[0m[0082] Cmd: /bin/sh                                 
Apr 01 19:02:13 [celery-beat] [34m│[0m [36mINFO[0m[0082] Args: [-c DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true] 
Apr 01 19:02:13 [celery-beat] [34m│[0m [36mINFO[0m[0082] Running: [/bin/sh -c DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true] 
Apr 01 19:02:13 [api] [34m│[0m [36mINFO[0m[0081] Taking snapshot of files...                  
Apr 01 19:02:13 [migrate] [34m│[0m [36mINFO[0m[0081] Taking snapshot of files...                  
Apr 01 19:02:13 [api] [34m│[0m [36mINFO[0m[0081] Pushing layer <registry-uri-4> to cache now 
Apr 01 19:02:13 [api] [34m│[0m [36mINFO[0m[0081] Pushing image to <registry-uri-5> 
Apr 01 19:02:13 [api] [34m│[0m [36mINFO[0m[0081] EXPOSE 8000                                  
Apr 01 19:02:13 [api] [34m│[0m [36mINFO[0m[0081] Cmd: EXPOSE                                  
Apr 01 19:02:13 [api] [34m│[0m [36mINFO[0m[0081] Adding exposed port: 8000/tcp                
Apr 01 19:02:13 [api] [34m│[0m [36mINFO[0m[0081] No files changed in this command, skipping snapshotting. 
Apr 01 19:02:13 [migrate] [34m│[0m [36mINFO[0m[0082] Pushing layer <registry-uri-4> to cache now 
Apr 01 19:02:13 [migrate] [34m│[0m [36mINFO[0m[0082] Pushing image to <registry-uri-5> 
Apr 01 19:02:13 [migrate] [34m│[0m [36mINFO[0m[0082] EXPOSE 8000                                  
Apr 01 19:02:13 [migrate] [34m│[0m [36mINFO[0m[0082] Cmd: EXPOSE                                  
Apr 01 19:02:13 [migrate] [34m│[0m [36mINFO[0m[0082] Adding exposed port: 8000/tcp                
Apr 01 19:02:13 [migrate] [34m│[0m [36mINFO[0m[0082] No files changed in this command, skipping snapshotting. 
Apr 01 19:02:14 [celery-beat] [34m│[0m 
Apr 01 19:02:14 [celery-beat] [34m│[0m 168 static files copied to '/app/staticfiles', 168 post-processed.
Apr 01 19:02:14 [api] [34m│[0m [36mINFO[0m[0082] Pushed <registry-uri-6> 
Apr 01 19:02:14 [api] [34m│[0m [36mINFO[0m[0082] Pushing image to <image-7> 
Apr 01 19:02:14 [migrate] [34m│[0m [36mINFO[0m[0083] Pushed <registry-uri-6> 
Apr 01 19:02:14 [migrate] [34m│[0m [36mINFO[0m[0083] Pushing image to <image-7> 
Apr 01 19:02:15 [celery-beat] [34m│[0m [36mINFO[0m[0084] Taking snapshot of files...                  
Apr 01 19:02:15 [celery-beat] [34m│[0m [36mINFO[0m[0084] Pushing layer <registry-uri-4> to cache now 
Apr 01 19:02:15 [celery-beat] [34m│[0m [36mINFO[0m[0084] Pushing image to <registry-uri-5> 
Apr 01 19:02:15 [celery-beat] [34m│[0m [36mINFO[0m[0084] EXPOSE 8000                                  
Apr 01 19:02:15 [celery-beat] [34m│[0m [36mINFO[0m[0084] Cmd: EXPOSE                                  
Apr 01 19:02:15 [celery-beat] [34m│[0m [36mINFO[0m[0084] Adding exposed port: 8000/tcp                
Apr 01 19:02:15 [celery-beat] [34m│[0m [36mINFO[0m[0084] No files changed in this command, skipping snapshotting. 
Apr 01 19:02:16 [celery-beat] [34m│[0m [36mINFO[0m[0085] Pushed <registry-uri-6> 
Apr 01 19:02:16 [celery-beat] [34m│[0m [36mINFO[0m[0085] Pushing image to <image-7> 
Apr 01 19:02:16 [migrate] [34m│[0m [36mINFO[0m[0085] Pushed <registry-uri-8> 
Apr 01 19:02:16 [migrate] [34m│[0m 
Apr 01 19:02:17 [migrate] [34m│[0m [32m ✔ built and uploaded app container image to DOCR[0m
Apr 01 19:02:17 [migrate] [34m╰──────────────────────────────────────────╼[0m
Apr 01 19:02:17 [migrate] 
Apr 01 19:02:17 [migrate] [32m ✔ [0m[30m[42m build complete [0m[0m
Apr 01 19:02:17 [migrate] 
Apr 01 19:02:17 [api] [34m│[0m [36mINFO[0m[0085] Pushed <registry-uri-8> 
Apr 01 19:02:17 [api] [34m│[0m 
Apr 01 19:02:18 [api] [34m│[0m [32m ✔ built and uploaded app container image to DOCR[0m
Apr 01 19:02:18 [api] [34m╰──────────────────────────────────────────╼[0m
Apr 01 19:02:18 [api] 
Apr 01 19:02:18 [api] [32m ✔ [0m[30m[42m build complete [0m[0m
Apr 01 19:02:18 [api] 
Apr 01 19:02:18 [celery-worker] [34m│[0m [36mINFO[0m[0085] COPY . .                                     
Apr 01 19:02:18 [celery-worker] [34m│[0m [36mINFO[0m[0085] Taking snapshot of files...                  
Apr 01 19:02:18 [celery-beat] [34m│[0m [36mINFO[0m[0087] Pushed <registry-uri-8> 
Apr 01 19:02:18 [celery-beat] [34m│[0m 
Apr 01 19:02:19 [celery-beat] [34m│[0m [32m ✔ built and uploaded app container image to DOCR[0m
Apr 01 19:02:19 [celery-beat] [34m╰──────────────────────────────────────────╼[0m
Apr 01 19:02:19 [celery-beat] 
Apr 01 19:02:19 [celery-beat] [32m ✔ [0m[30m[42m build complete [0m[0m
Apr 01 19:02:19 [celery-beat] 
Apr 01 19:02:19 [celery-worker] [34m│[0m [36mINFO[0m[0086] RUN DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true 
Apr 01 19:02:20 [celery-worker] [34m│[0m [36mINFO[0m[0087] Cmd: /bin/sh                                 
Apr 01 19:02:20 [celery-worker] [34m│[0m [36mINFO[0m[0087] Args: [-c DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true] 
Apr 01 19:02:20 [celery-worker] [34m│[0m [36mINFO[0m[0087] Running: [/bin/sh -c DJANGO_SETTINGS_MODULE=config.settings.staging     SECRET_KEY=build-phase-dummy     DB_HOST=localhost DB_NAME=x DB_USER=x DB_PASSWORD=x     python manage.py collectstatic --noinput || true] 
Apr 01 19:02:21 [celery-worker] [34m│[0m 
Apr 01 19:02:21 [celery-worker] [34m│[0m 168 static files copied to '/app/staticfiles', 168 post-processed.
Apr 01 19:02:22 [celery-worker] [34m│[0m [36mINFO[0m[0089] Taking snapshot of files...                  
Apr 01 19:02:22 [celery-worker] [34m│[0m [36mINFO[0m[0089] EXPOSE 8000                                  
Apr 01 19:02:22 [celery-worker] [34m│[0m [36mINFO[0m[0089] Cmd: EXPOSE                                  
Apr 01 19:02:22 [celery-worker] [34m│[0m [36mINFO[0m[0089] Adding exposed port: 8000/tcp                
Apr 01 19:02:22 [celery-worker] [34m│[0m [36mINFO[0m[0089] No files changed in this command, skipping snapshotting. 
Apr 01 19:02:22 [celery-worker] [34m│[0m [36mINFO[0m[0089] Pushing layer <registry-uri-4> to cache now 
Apr 01 19:02:22 [celery-worker] [34m│[0m [36mINFO[0m[0089] Pushing image to <registry-uri-5> 
Apr 01 19:02:23 [celery-worker] [34m│[0m [36mINFO[0m[0090] Pushed <registry-uri-6> 
Apr 01 19:02:23 [celery-worker] [34m│[0m [36mINFO[0m[0090] Pushing image to <image-7> 
Apr 01 19:02:25 [celery-worker] [34m│[0m [36mINFO[0m[0092] Pushed <registry-uri-8> 
Apr 01 19:02:25 [celery-worker] [34m│[0m 
Apr 01 19:02:25 [celery-worker] [34m│[0m [32m ✔ built and uploaded app container image to DOCR[0m
Apr 01 19:02:25 [celery-worker] [34m╰──────────────────────────────────────────╼[0m
Apr 01 19:02:25 [celery-worker] 
Apr 01 19:02:25 [celery-worker] [32m ✔ [0m[30m[42m build complete [0m[0m
Apr 01 19:02:25 [celery-worker] 
Apr 01 19:03:48 [celery-beat] celery beat v5.3.6 (emerald-rush) is starting.
Apr 01 19:03:49 [api] [2026-04-01 19:03:49 +0000] [1] [INFO] Starting gunicorn 21.2.0
Apr 01 19:03:49 [api] [2026-04-01 19:03:49 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
Apr 01 19:03:49 [api] [2026-04-01 19:03:49 +0000] [1] [INFO] Using worker: gthread
Apr 01 19:03:49 [api] [2026-04-01 19:03:49 +0000] [2] [INFO] Booting worker with pid: 2
Apr 01 19:03:49 [api] [2026-04-01 19:03:49 +0000] [3] [INFO] Booting worker with pid: 3
Apr 01 19:03:51 [celery-beat] Traceback (most recent call last):
Apr 01 19:03:51 [celery-beat]   File "/usr/local/bin/celery", line 8, in <module>
Apr 01 19:03:51 [celery-beat]     sys.exit(main())
Apr 01 19:03:51 [celery-beat]              ^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/__main__.py", line 15, in main
Apr 01 19:03:51 [celery-beat]     sys.exit(_main())
Apr 01 19:03:51 [celery-beat]              ^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/celery.py", line 236, in main
Apr 01 19:03:51 [celery-beat]     return celery(auto_envvar_prefix="CELERY")
Apr 01 19:03:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1485, in __call__
Apr 01 19:03:51 [celery-beat]     return self.main(*args, **kwargs)
Apr 01 19:03:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1406, in main
Apr 01 19:03:51 [celery-beat]     rv = self.invoke(ctx)
Apr 01 19:03:51 [celery-beat]          ^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1873, in invoke
Apr 01 19:03:51 [celery-beat]     return _process_result(sub_ctx.command.invoke(sub_ctx))
Apr 01 19:03:51 [celery-beat]                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1269, in invoke
Apr 01 19:03:51 [celery-beat]     return ctx.invoke(self.callback, **ctx.params)
Apr 01 19:03:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 824, in invoke
Apr 01 19:03:51 [celery-beat]     return callback(*args, **kwargs)
Apr 01 19:03:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/decorators.py", line 34, in new_func
Apr 01 19:03:51 [celery-beat]     return f(get_current_context(), *args, **kwargs)
Apr 01 19:03:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/base.py", line 134, in caller
Apr 01 19:03:51 [celery-beat]     return f(ctx, *args, **kwargs)
Apr 01 19:03:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/beat.py", line 72, in beat
Apr 01 19:03:51 [celery-beat]     return beat().run()
Apr 01 19:03:51 [celery-beat]            ^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 84, in run
Apr 01 19:03:51 [celery-beat]     self.start_scheduler()
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 104, in start_scheduler
Apr 01 19:03:51 [celery-beat]     print(self.banner(service))
Apr 01 19:03:51 [celery-beat]           ^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 126, in banner
Apr 01 19:03:51 [celery-beat]     c.reset(self.startup_info(service))),
Apr 01 19:03:51 [celery-beat]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 136, in startup_info
Apr 01 19:03:51 [celery-beat]     scheduler = service.get_scheduler(lazy=True)
Apr 01 19:03:51 [celery-beat]                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/beat.py", line 668, in get_scheduler
Apr 01 19:03:51 [celery-beat]     return symbol_by_name(self.scheduler_cls, aliases=aliases)(
Apr 01 19:03:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/kombu/utils/imports.py", line 59, in symbol_by_name
Apr 01 19:03:51 [celery-beat]     module = imp(module_name, package=package, **kwargs)
Apr 01 19:03:51 [celery-beat]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
Apr 01 19:03:51 [celery-beat]     return _bootstrap._gcd_import(name[level:], package, level)
Apr 01 19:03:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
Apr 01 19:03:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
Apr 01 19:03:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
Apr 01 19:03:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
Apr 01 19:03:51 [celery-beat]   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
Apr 01 19:03:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/schedulers.py", line 19, in <module>
Apr 01 19:03:51 [celery-beat]     from .models import (ClockedSchedule, CrontabSchedule, IntervalSchedule,
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/models.py", line 78, in <module>
Apr 01 19:03:51 [celery-beat]     class SolarSchedule(models.Model):
Apr 01 19:03:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django/db/models/base.py", line 134, in __new__
Apr 01 19:03:51 [celery-beat]     raise RuntimeError(
Apr 01 19:03:51 [celery-beat] RuntimeError: Model class django_celery_beat.models.SolarSchedule doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
Apr 01 19:03:52 [celery-worker] /usr/local/lib/python3.11/site-packages/celery/platforms.py:829: SecurityWarning: You're running the worker with superuser privileges: this is
Apr 01 19:03:52 [celery-worker] absolutely not recommended!
Apr 01 19:03:52 [celery-worker] 
Apr 01 19:03:52 [celery-worker] Please specify a different user using the --uid option.
Apr 01 19:03:52 [celery-worker] 
Apr 01 19:03:52 [celery-worker] User information: uid=0 euid=0 gid=0 egid=0
Apr 01 19:03:52 [celery-worker] 
Apr 01 19:03:52 [celery-worker]   warnings.warn(SecurityWarning(ROOT_DISCOURAGED.format(
Apr 01 19:03:52 [celery-worker] Unrecoverable error: ValueError('\nA rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE\n')
Apr 01 19:03:52 [celery-worker] Traceback (most recent call last):
Apr 01 19:03:52 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/worker/worker.py", line 202, in start
Apr 01 19:03:52 [celery-worker]     self.blueprint.start(self)
Apr 01 19:03:52 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/bootsteps.py", line 112, in start
Apr 01 19:03:52 [celery-worker]     self.on_start()
Apr 01 19:03:52 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 135, in on_start
Apr 01 19:03:52 [celery-worker]     self.emit_banner()
Apr 01 19:03:52 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 169, in emit_banner
Apr 01 19:03:52 [celery-worker]     ' \n', self.startup_info(artlines=not use_image))),
Apr 01 19:03:52 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:52 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 231, in startup_info
Apr 01 19:03:52 [celery-worker]     results=self.app.backend.as_uri(),
Apr 01 19:03:52 [celery-worker]             ^^^^^^^^^^^^^^^^
Apr 01 19:03:52 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 1301, in backend
Apr 01 19:03:52 [celery-worker]     self._backend = self._get_backend()
Apr 01 19:03:52 [celery-worker]                     ^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:52 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 969, in _get_backend
Apr 01 19:03:52 [celery-worker]     return backend(app=self, url=url)
Apr 01 19:03:52 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:52 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/backends/redis.py", line 289, in __init__
Apr 01 19:03:52 [celery-worker]     raise ValueError(E_REDIS_SSL_CERT_REQS_MISSING_INVALID)
Apr 01 19:03:52 [celery-worker] ValueError: 
Apr 01 19:03:52 [celery-worker] A rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE
Apr 01 19:03:52 [celery-worker] 
Apr 01 19:03:52 [celery-beat] ERROR component celery-beat exited with code: 1
Apr 01 19:03:54 [celery-beat] celery beat v5.3.6 (emerald-rush) is starting.
Apr 01 19:03:52 [celery-worker] ERROR component celery-worker exited with code: 1
Apr 01 19:03:57 [celery-beat] Traceback (most recent call last):
Apr 01 19:03:57 [celery-beat]   File "/usr/local/bin/celery", line 8, in <module>
Apr 01 19:03:57 [celery-beat]     sys.exit(main())
Apr 01 19:03:57 [celery-beat]              ^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/__main__.py", line 15, in main
Apr 01 19:03:57 [celery-beat]     sys.exit(_main())
Apr 01 19:03:57 [celery-beat]              ^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/celery.py", line 236, in main
Apr 01 19:03:57 [celery-beat]     return celery(auto_envvar_prefix="CELERY")
Apr 01 19:03:57 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1485, in __call__
Apr 01 19:03:57 [celery-beat]     return self.main(*args, **kwargs)
Apr 01 19:03:57 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1406, in main
Apr 01 19:03:57 [celery-beat]     rv = self.invoke(ctx)
Apr 01 19:03:57 [celery-beat]          ^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1873, in invoke
Apr 01 19:03:57 [celery-beat]     return _process_result(sub_ctx.command.invoke(sub_ctx))
Apr 01 19:03:57 [celery-beat]                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1269, in invoke
Apr 01 19:03:57 [celery-beat]     return ctx.invoke(self.callback, **ctx.params)
Apr 01 19:03:57 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 824, in invoke
Apr 01 19:03:57 [celery-beat]     return callback(*args, **kwargs)
Apr 01 19:03:57 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/decorators.py", line 34, in new_func
Apr 01 19:03:57 [celery-beat]     return f(get_current_context(), *args, **kwargs)
Apr 01 19:03:57 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/base.py", line 134, in caller
Apr 01 19:03:57 [celery-beat]     return f(ctx, *args, **kwargs)
Apr 01 19:03:57 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/beat.py", line 72, in beat
Apr 01 19:03:57 [celery-beat]     return beat().run()
Apr 01 19:03:57 [celery-beat]            ^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 84, in run
Apr 01 19:03:57 [celery-beat]     self.start_scheduler()
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 104, in start_scheduler
Apr 01 19:03:57 [celery-beat]     print(self.banner(service))
Apr 01 19:03:57 [celery-beat]           ^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 126, in banner
Apr 01 19:03:57 [celery-beat]     c.reset(self.startup_info(service))),
Apr 01 19:03:57 [celery-beat]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 136, in startup_info
Apr 01 19:03:57 [celery-beat]     scheduler = service.get_scheduler(lazy=True)
Apr 01 19:03:57 [celery-beat]                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/beat.py", line 668, in get_scheduler
Apr 01 19:03:57 [celery-beat]     return symbol_by_name(self.scheduler_cls, aliases=aliases)(
Apr 01 19:03:57 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/kombu/utils/imports.py", line 59, in symbol_by_name
Apr 01 19:03:57 [celery-beat]     module = imp(module_name, package=package, **kwargs)
Apr 01 19:03:57 [celery-beat]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
Apr 01 19:03:57 [celery-beat]     return _bootstrap._gcd_import(name[level:], package, level)
Apr 01 19:03:57 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:57 [celery-beat]   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
Apr 01 19:03:57 [celery-beat]   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
Apr 01 19:03:57 [celery-beat]   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
Apr 01 19:03:57 [celery-beat]   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
Apr 01 19:03:57 [celery-beat]   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
Apr 01 19:03:57 [celery-beat]   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/schedulers.py", line 19, in <module>
Apr 01 19:03:57 [celery-beat]     from .models import (ClockedSchedule, CrontabSchedule, IntervalSchedule,
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/models.py", line 78, in <module>
Apr 01 19:03:57 [celery-beat]     class SolarSchedule(models.Model):
Apr 01 19:03:57 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django/db/models/base.py", line 134, in __new__
Apr 01 19:03:57 [celery-beat]     raise RuntimeError(
Apr 01 19:03:57 [celery-beat] RuntimeError: Model class django_celery_beat.models.SolarSchedule doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
Apr 01 19:03:58 [celery-worker] /usr/local/lib/python3.11/site-packages/celery/platforms.py:829: SecurityWarning: You're running the worker with superuser privileges: this is
Apr 01 19:03:58 [celery-worker] absolutely not recommended!
Apr 01 19:03:58 [celery-worker] 
Apr 01 19:03:58 [celery-worker] Please specify a different user using the --uid option.
Apr 01 19:03:58 [celery-worker] 
Apr 01 19:03:58 [celery-worker] User information: uid=0 euid=0 gid=0 egid=0
Apr 01 19:03:58 [celery-worker] 
Apr 01 19:03:58 [celery-worker]   warnings.warn(SecurityWarning(ROOT_DISCOURAGED.format(
Apr 01 19:03:58 [celery-worker] Unrecoverable error: ValueError('\nA rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE\n')
Apr 01 19:03:58 [celery-worker] Traceback (most recent call last):
Apr 01 19:03:58 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/worker/worker.py", line 202, in start
Apr 01 19:03:58 [celery-worker]     self.blueprint.start(self)
Apr 01 19:03:58 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/bootsteps.py", line 112, in start
Apr 01 19:03:58 [celery-worker]     self.on_start()
Apr 01 19:03:58 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 135, in on_start
Apr 01 19:03:58 [celery-worker]     self.emit_banner()
Apr 01 19:03:58 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 169, in emit_banner
Apr 01 19:03:58 [celery-worker]     ' \n', self.startup_info(artlines=not use_image))),
Apr 01 19:03:58 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:58 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 231, in startup_info
Apr 01 19:03:58 [celery-worker]     results=self.app.backend.as_uri(),
Apr 01 19:03:58 [celery-worker]             ^^^^^^^^^^^^^^^^
Apr 01 19:03:58 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 1301, in backend
Apr 01 19:03:58 [celery-worker]     self._backend = self._get_backend()
Apr 01 19:03:58 [celery-worker]                     ^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:58 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 969, in _get_backend
Apr 01 19:03:58 [celery-worker]     return backend(app=self, url=url)
Apr 01 19:03:58 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:03:58 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/backends/redis.py", line 289, in __init__
Apr 01 19:03:58 [celery-worker]     raise ValueError(E_REDIS_SSL_CERT_REQS_MISSING_INVALID)
Apr 01 19:03:58 [celery-worker] ValueError: 
Apr 01 19:03:58 [celery-worker] A rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE
Apr 01 19:03:58 [celery-worker] 
Apr 01 19:03:59 [celery-worker] ERROR component celery-worker exited with code: 1
Apr 01 19:03:58 [celery-beat] ERROR component celery-beat exited with code: 1
Apr 01 19:04:16 [celery-beat] celery beat v5.3.6 (emerald-rush) is starting.
Apr 01 19:04:16 [celery-worker] /usr/local/lib/python3.11/site-packages/celery/platforms.py:829: SecurityWarning: You're running the worker with superuser privileges: this is
Apr 01 19:04:16 [celery-worker] absolutely not recommended!
Apr 01 19:04:16 [celery-worker] 
Apr 01 19:04:16 [celery-worker] Please specify a different user using the --uid option.
Apr 01 19:04:16 [celery-worker] 
Apr 01 19:04:16 [celery-worker] User information: uid=0 euid=0 gid=0 egid=0
Apr 01 19:04:16 [celery-worker] 
Apr 01 19:04:16 [celery-worker]   warnings.warn(SecurityWarning(ROOT_DISCOURAGED.format(
Apr 01 19:04:16 [celery-worker] Unrecoverable error: ValueError('\nA rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE\n')
Apr 01 19:04:16 [celery-worker] Traceback (most recent call last):
Apr 01 19:04:16 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/worker/worker.py", line 202, in start
Apr 01 19:04:16 [celery-worker]     self.blueprint.start(self)
Apr 01 19:04:16 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/bootsteps.py", line 112, in start
Apr 01 19:04:16 [celery-worker]     self.on_start()
Apr 01 19:04:16 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 135, in on_start
Apr 01 19:04:16 [celery-worker]     self.emit_banner()
Apr 01 19:04:16 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 169, in emit_banner
Apr 01 19:04:16 [celery-worker]     ' \n', self.startup_info(artlines=not use_image))),
Apr 01 19:04:16 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:16 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 231, in startup_info
Apr 01 19:04:16 [celery-worker]     results=self.app.backend.as_uri(),
Apr 01 19:04:16 [celery-worker]             ^^^^^^^^^^^^^^^^
Apr 01 19:04:16 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 1301, in backend
Apr 01 19:04:16 [celery-worker]     self._backend = self._get_backend()
Apr 01 19:04:16 [celery-worker]                     ^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:16 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 969, in _get_backend
Apr 01 19:04:16 [celery-worker]     return backend(app=self, url=url)
Apr 01 19:04:16 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:16 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/backends/redis.py", line 289, in __init__
Apr 01 19:04:16 [celery-worker]     raise ValueError(E_REDIS_SSL_CERT_REQS_MISSING_INVALID)
Apr 01 19:04:16 [celery-worker] ValueError: 
Apr 01 19:04:16 [celery-worker] A rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE
Apr 01 19:04:16 [celery-worker] 
Apr 01 19:04:19 [celery-beat] Traceback (most recent call last):
Apr 01 19:04:19 [celery-beat]   File "/usr/local/bin/celery", line 8, in <module>
Apr 01 19:04:19 [celery-beat]     sys.exit(main())
Apr 01 19:04:19 [celery-beat]              ^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/__main__.py", line 15, in main
Apr 01 19:04:19 [celery-beat]     sys.exit(_main())
Apr 01 19:04:19 [celery-beat]              ^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/celery.py", line 236, in main
Apr 01 19:04:19 [celery-beat]     return celery(auto_envvar_prefix="CELERY")
Apr 01 19:04:19 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1485, in __call__
Apr 01 19:04:19 [celery-beat]     return self.main(*args, **kwargs)
Apr 01 19:04:19 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1406, in main
Apr 01 19:04:19 [celery-beat]     rv = self.invoke(ctx)
Apr 01 19:04:19 [celery-beat]          ^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1873, in invoke
Apr 01 19:04:19 [celery-beat]     return _process_result(sub_ctx.command.invoke(sub_ctx))
Apr 01 19:04:19 [celery-beat]                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1269, in invoke
Apr 01 19:04:19 [celery-beat]     return ctx.invoke(self.callback, **ctx.params)
Apr 01 19:04:19 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 824, in invoke
Apr 01 19:04:19 [celery-beat]     return callback(*args, **kwargs)
Apr 01 19:04:19 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/decorators.py", line 34, in new_func
Apr 01 19:04:19 [celery-beat]     return f(get_current_context(), *args, **kwargs)
Apr 01 19:04:19 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/base.py", line 134, in caller
Apr 01 19:04:19 [celery-beat]     return f(ctx, *args, **kwargs)
Apr 01 19:04:19 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/beat.py", line 72, in beat
Apr 01 19:04:19 [celery-beat]     return beat().run()
Apr 01 19:04:19 [celery-beat]            ^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 84, in run
Apr 01 19:04:19 [celery-beat]     self.start_scheduler()
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 104, in start_scheduler
Apr 01 19:04:19 [celery-beat]     print(self.banner(service))
Apr 01 19:04:19 [celery-beat]           ^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 126, in banner
Apr 01 19:04:19 [celery-beat]     c.reset(self.startup_info(service))),
Apr 01 19:04:19 [celery-beat]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 136, in startup_info
Apr 01 19:04:19 [celery-beat]     scheduler = service.get_scheduler(lazy=True)
Apr 01 19:04:19 [celery-beat]                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/beat.py", line 668, in get_scheduler
Apr 01 19:04:19 [celery-beat]     return symbol_by_name(self.scheduler_cls, aliases=aliases)(
Apr 01 19:04:19 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/kombu/utils/imports.py", line 59, in symbol_by_name
Apr 01 19:04:19 [celery-beat]     module = imp(module_name, package=package, **kwargs)
Apr 01 19:04:19 [celery-beat]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
Apr 01 19:04:19 [celery-beat]     return _bootstrap._gcd_import(name[level:], package, level)
Apr 01 19:04:19 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:19 [celery-beat]   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
Apr 01 19:04:19 [celery-beat]   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
Apr 01 19:04:19 [celery-beat]   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
Apr 01 19:04:19 [celery-beat]   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
Apr 01 19:04:19 [celery-beat]   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
Apr 01 19:04:19 [celery-beat]   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/schedulers.py", line 19, in <module>
Apr 01 19:04:19 [celery-beat]     from .models import (ClockedSchedule, CrontabSchedule, IntervalSchedule,
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/models.py", line 78, in <module>
Apr 01 19:04:19 [celery-beat]     class SolarSchedule(models.Model):
Apr 01 19:04:19 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django/db/models/base.py", line 134, in __new__
Apr 01 19:04:19 [celery-beat]     raise RuntimeError(
Apr 01 19:04:19 [celery-beat] RuntimeError: Model class django_celery_beat.models.SolarSchedule doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
Apr 01 19:04:17 [celery-worker] ERROR component celery-worker exited with code: 1
Apr 01 19:04:46 [celery-worker] /usr/local/lib/python3.11/site-packages/celery/platforms.py:829: SecurityWarning: You're running the worker with superuser privileges: this is
Apr 01 19:04:46 [celery-worker] absolutely not recommended!
Apr 01 19:04:46 [celery-worker] 
Apr 01 19:04:46 [celery-worker] Please specify a different user using the --uid option.
Apr 01 19:04:46 [celery-worker] 
Apr 01 19:04:46 [celery-worker] User information: uid=0 euid=0 gid=0 egid=0
Apr 01 19:04:46 [celery-worker] 
Apr 01 19:04:46 [celery-worker]   warnings.warn(SecurityWarning(ROOT_DISCOURAGED.format(
Apr 01 19:04:46 [celery-worker] Unrecoverable error: ValueError('\nA rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE\n')
Apr 01 19:04:46 [celery-worker] Traceback (most recent call last):
Apr 01 19:04:46 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/worker/worker.py", line 202, in start
Apr 01 19:04:46 [celery-worker]     self.blueprint.start(self)
Apr 01 19:04:46 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/bootsteps.py", line 112, in start
Apr 01 19:04:46 [celery-worker]     self.on_start()
Apr 01 19:04:46 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 135, in on_start
Apr 01 19:04:46 [celery-worker]     self.emit_banner()
Apr 01 19:04:46 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 169, in emit_banner
Apr 01 19:04:46 [celery-worker]     ' \n', self.startup_info(artlines=not use_image))),
Apr 01 19:04:46 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:46 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 231, in startup_info
Apr 01 19:04:46 [celery-worker]     results=self.app.backend.as_uri(),
Apr 01 19:04:46 [celery-worker]             ^^^^^^^^^^^^^^^^
Apr 01 19:04:46 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 1301, in backend
Apr 01 19:04:46 [celery-worker]     self._backend = self._get_backend()
Apr 01 19:04:46 [celery-worker]                     ^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:46 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 969, in _get_backend
Apr 01 19:04:46 [celery-worker]     return backend(app=self, url=url)
Apr 01 19:04:46 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:46 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/backends/redis.py", line 289, in __init__
Apr 01 19:04:46 [celery-worker]     raise ValueError(E_REDIS_SSL_CERT_REQS_MISSING_INVALID)
Apr 01 19:04:46 [celery-worker] ValueError: 
Apr 01 19:04:46 [celery-worker] A rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE
Apr 01 19:04:46 [celery-worker] 
Apr 01 19:04:19 [celery-beat] ERROR component celery-beat exited with code: 1
Apr 01 19:04:48 [celery-beat] celery beat v5.3.6 (emerald-rush) is starting.
Apr 01 19:04:51 [celery-beat] Traceback (most recent call last):
Apr 01 19:04:51 [celery-beat]   File "/usr/local/bin/celery", line 8, in <module>
Apr 01 19:04:51 [celery-beat]     sys.exit(main())
Apr 01 19:04:51 [celery-beat]              ^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/__main__.py", line 15, in main
Apr 01 19:04:51 [celery-beat]     sys.exit(_main())
Apr 01 19:04:51 [celery-beat]              ^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/celery.py", line 236, in main
Apr 01 19:04:51 [celery-beat]     return celery(auto_envvar_prefix="CELERY")
Apr 01 19:04:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1485, in __call__
Apr 01 19:04:51 [celery-beat]     return self.main(*args, **kwargs)
Apr 01 19:04:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1406, in main
Apr 01 19:04:51 [celery-beat]     rv = self.invoke(ctx)
Apr 01 19:04:51 [celery-beat]          ^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1873, in invoke
Apr 01 19:04:51 [celery-beat]     return _process_result(sub_ctx.command.invoke(sub_ctx))
Apr 01 19:04:51 [celery-beat]                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1269, in invoke
Apr 01 19:04:51 [celery-beat]     return ctx.invoke(self.callback, **ctx.params)
Apr 01 19:04:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 824, in invoke
Apr 01 19:04:51 [celery-beat]     return callback(*args, **kwargs)
Apr 01 19:04:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/decorators.py", line 34, in new_func
Apr 01 19:04:51 [celery-beat]     return f(get_current_context(), *args, **kwargs)
Apr 01 19:04:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/base.py", line 134, in caller
Apr 01 19:04:51 [celery-beat]     return f(ctx, *args, **kwargs)
Apr 01 19:04:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/beat.py", line 72, in beat
Apr 01 19:04:51 [celery-beat]     return beat().run()
Apr 01 19:04:51 [celery-beat]            ^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 84, in run
Apr 01 19:04:51 [celery-beat]     self.start_scheduler()
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 104, in start_scheduler
Apr 01 19:04:51 [celery-beat]     print(self.banner(service))
Apr 01 19:04:51 [celery-beat]           ^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 126, in banner
Apr 01 19:04:51 [celery-beat]     c.reset(self.startup_info(service))),
Apr 01 19:04:51 [celery-beat]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 136, in startup_info
Apr 01 19:04:51 [celery-beat]     scheduler = service.get_scheduler(lazy=True)
Apr 01 19:04:51 [celery-beat]                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/beat.py", line 668, in get_scheduler
Apr 01 19:04:51 [celery-beat]     return symbol_by_name(self.scheduler_cls, aliases=aliases)(
Apr 01 19:04:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/kombu/utils/imports.py", line 59, in symbol_by_name
Apr 01 19:04:51 [celery-beat]     module = imp(module_name, package=package, **kwargs)
Apr 01 19:04:51 [celery-beat]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
Apr 01 19:04:51 [celery-beat]     return _bootstrap._gcd_import(name[level:], package, level)
Apr 01 19:04:51 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:04:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
Apr 01 19:04:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
Apr 01 19:04:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
Apr 01 19:04:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
Apr 01 19:04:51 [celery-beat]   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
Apr 01 19:04:51 [celery-beat]   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/schedulers.py", line 19, in <module>
Apr 01 19:04:51 [celery-beat]     from .models import (ClockedSchedule, CrontabSchedule, IntervalSchedule,
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/models.py", line 78, in <module>
Apr 01 19:04:51 [celery-beat]     class SolarSchedule(models.Model):
Apr 01 19:04:51 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django/db/models/base.py", line 134, in __new__
Apr 01 19:04:51 [celery-beat]     raise RuntimeError(
Apr 01 19:04:51 [celery-beat] RuntimeError: Model class django_celery_beat.models.SolarSchedule doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
Apr 01 19:04:51 [api] {"asctime": "2026-04-01 18:04:51,683", "levelname": "ERROR", "name": "django.security.DisallowedHost", "message": "Invalid HTTP_HOST header: '100.127.2.14:8000'. You may need to add '100.127.2.14' to ALLOWED_HOSTS.", "exc_info": "Traceback (most recent call last):\n  File \"/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py\", line 55, in inner\n    response = get_response(request)\n               ^^^^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py\", line 133, in __call__\n    response = self.process_request(request)\n               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.11/site-packages/django/middleware/common.py\", line 48, in process_request\n    host = request.get_host()\n           ^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.11/site-packages/django/http/request.py\", line 150, in get_host\n    raise DisallowedHost(msg)\ndjango.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: '100.127.2.14:8000'. You may need to add '100.127.2.14' to ALLOWED_HOSTS.", "status_code": 400, "request": "<WSGIRequest: GET '/api/v1/health/'>"}
Apr 01 19:04:51 [api] {"asctime": "2026-04-01 18:04:51,708", "levelname": "WARNING", "name": "django.request", "message": "Bad Request: /api/v1/health/", "status_code": 400, "request": "<WSGIRequest: GET '/api/v1/health/'>"}
Apr 01 19:05:10 [api] {"asctime": "2026-04-01 18:05:10,530", "levelname": "ERROR", "name": "django.security.DisallowedHost", "message": "Invalid HTTP_HOST header: '100.127.2.14:8000'. You may need to add '100.127.2.14' to ALLOWED_HOSTS.", "exc_info": "Traceback (most recent call last):\n  File \"/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py\", line 55, in inner\n    response = get_response(request)\n               ^^^^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py\", line 133, in __call__\n    response = self.process_request(request)\n               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.11/site-packages/django/middleware/common.py\", line 48, in process_request\n    host = request.get_host()\n           ^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.11/site-packages/django/http/request.py\", line 150, in get_host\n    raise DisallowedHost(msg)\ndjango.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: '100.127.2.14:8000'. You may need to add '100.127.2.14' to ALLOWED_HOSTS.", "status_code": 400, "request": "<WSGIRequest: GET '/api/v1/health/'>"}
Apr 01 19:05:10 [api] {"asctime": "2026-04-01 18:05:10,535", "levelname": "WARNING", "name": "django.request", "message": "Bad Request: /api/v1/health/", "status_code": 400, "request": "<WSGIRequest: GET '/api/v1/health/'>"}
Apr 01 19:04:46 [celery-worker] ERROR component celery-worker exited with code: 1
Apr 01 19:05:41 [api] {"asctime": "2026-04-01 18:05:41,642", "levelname": "ERROR", "name": "django.security.DisallowedHost", "message": "Invalid HTTP_HOST header: '100.127.2.14:8000'. You may need to add '100.127.2.14' to ALLOWED_HOSTS.", "exc_info": "Traceback (most recent call last):\n  File \"/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py\", line 55, in inner\n    response = get_response(request)\n               ^^^^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py\", line 133, in __call__\n    response = self.process_request(request)\n               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.11/site-packages/django/middleware/common.py\", line 48, in process_request\n    host = request.get_host()\n           ^^^^^^^^^^^^^^^^^^\n  File \"/usr/local/lib/python3.11/site-packages/django/http/request.py\", line 150, in get_host\n    raise DisallowedHost(msg)\ndjango.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: '100.127.2.14:8000'. You may need to add '100.127.2.14' to ALLOWED_HOSTS.", "status_code": 400, "request": "<WSGIRequest: GET '/api/v1/health/'>"}
Apr 01 19:05:41 [api] {"asctime": "2026-04-01 18:05:41,659", "levelname": "WARNING", "name": "django.request", "message": "Bad Request: /api/v1/health/", "status_code": 400, "request": "<WSGIRequest: GET '/api/v1/health/'>"}
Apr 01 19:05:42 [celery-worker] /usr/local/lib/python3.11/site-packages/celery/platforms.py:829: SecurityWarning: You're running the worker with superuser privileges: this is
Apr 01 19:05:42 [celery-worker] absolutely not recommended!
Apr 01 19:05:42 [celery-worker] 
Apr 01 19:05:42 [celery-worker] Please specify a different user using the --uid option.
Apr 01 19:05:42 [celery-worker] 
Apr 01 19:05:42 [celery-worker] User information: uid=0 euid=0 gid=0 egid=0
Apr 01 19:05:42 [celery-worker] 
Apr 01 19:05:42 [celery-worker]   warnings.warn(SecurityWarning(ROOT_DISCOURAGED.format(
Apr 01 19:05:42 [celery-worker] Unrecoverable error: ValueError('\nA rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE\n')
Apr 01 19:05:42 [celery-worker] Traceback (most recent call last):
Apr 01 19:05:42 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/worker/worker.py", line 202, in start
Apr 01 19:05:42 [celery-worker]     self.blueprint.start(self)
Apr 01 19:05:42 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/bootsteps.py", line 112, in start
Apr 01 19:05:42 [celery-worker]     self.on_start()
Apr 01 19:05:42 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 135, in on_start
Apr 01 19:05:42 [celery-worker]     self.emit_banner()
Apr 01 19:05:42 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 169, in emit_banner
Apr 01 19:05:42 [celery-worker]     ' \n', self.startup_info(artlines=not use_image))),
Apr 01 19:05:42 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:42 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/apps/worker.py", line 231, in startup_info
Apr 01 19:05:42 [celery-worker]     results=self.app.backend.as_uri(),
Apr 01 19:05:42 [celery-worker]             ^^^^^^^^^^^^^^^^
Apr 01 19:05:42 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 1301, in backend
Apr 01 19:05:42 [celery-worker]     self._backend = self._get_backend()
Apr 01 19:05:42 [celery-worker]                     ^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:42 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/app/base.py", line 969, in _get_backend
Apr 01 19:05:42 [celery-worker]     return backend(app=self, url=url)
Apr 01 19:05:42 [celery-worker]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:42 [celery-worker]   File "/usr/local/lib/python3.11/site-packages/celery/backends/redis.py", line 289, in __init__
Apr 01 19:05:42 [celery-worker]     raise ValueError(E_REDIS_SSL_CERT_REQS_MISSING_INVALID)
Apr 01 19:05:42 [celery-worker] ValueError: 
Apr 01 19:05:42 [celery-worker] A rediss:// URL must have parameter ssl_cert_reqs and this must be set to CERT_REQUIRED, CERT_OPTIONAL, or CERT_NONE
Apr 01 19:05:42 [celery-worker] 
Apr 01 19:04:51 [celery-beat] ERROR component celery-beat exited with code: 1
Apr 01 19:05:45 [celery-beat] celery beat v5.3.6 (emerald-rush) is starting.
Apr 01 19:05:48 [celery-beat] Traceback (most recent call last):
Apr 01 19:05:48 [celery-beat]   File "/usr/local/bin/celery", line 8, in <module>
Apr 01 19:05:48 [celery-beat]     sys.exit(main())
Apr 01 19:05:48 [celery-beat]              ^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/__main__.py", line 15, in main
Apr 01 19:05:48 [celery-beat]     sys.exit(_main())
Apr 01 19:05:48 [celery-beat]              ^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/celery.py", line 236, in main
Apr 01 19:05:48 [celery-beat]     return celery(auto_envvar_prefix="CELERY")
Apr 01 19:05:48 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1485, in __call__
Apr 01 19:05:48 [celery-beat]     return self.main(*args, **kwargs)
Apr 01 19:05:48 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1406, in main
Apr 01 19:05:48 [celery-beat]     rv = self.invoke(ctx)
Apr 01 19:05:48 [celery-beat]          ^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1873, in invoke
Apr 01 19:05:48 [celery-beat]     return _process_result(sub_ctx.command.invoke(sub_ctx))
Apr 01 19:05:48 [celery-beat]                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1269, in invoke
Apr 01 19:05:48 [celery-beat]     return ctx.invoke(self.callback, **ctx.params)
Apr 01 19:05:48 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/core.py", line 824, in invoke
Apr 01 19:05:48 [celery-beat]     return callback(*args, **kwargs)
Apr 01 19:05:48 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/click/decorators.py", line 34, in new_func
Apr 01 19:05:48 [celery-beat]     return f(get_current_context(), *args, **kwargs)
Apr 01 19:05:48 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/base.py", line 134, in caller
Apr 01 19:05:48 [celery-beat]     return f(ctx, *args, **kwargs)
Apr 01 19:05:48 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/bin/beat.py", line 72, in beat
Apr 01 19:05:48 [celery-beat]     return beat().run()
Apr 01 19:05:48 [celery-beat]            ^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 84, in run
Apr 01 19:05:48 [celery-beat]     self.start_scheduler()
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 104, in start_scheduler
Apr 01 19:05:48 [celery-beat]     print(self.banner(service))
Apr 01 19:05:48 [celery-beat]           ^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 126, in banner
Apr 01 19:05:48 [celery-beat]     c.reset(self.startup_info(service))),
Apr 01 19:05:48 [celery-beat]             ^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/apps/beat.py", line 136, in startup_info
Apr 01 19:05:48 [celery-beat]     scheduler = service.get_scheduler(lazy=True)
Apr 01 19:05:48 [celery-beat]                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/celery/beat.py", line 668, in get_scheduler
Apr 01 19:05:48 [celery-beat]     return symbol_by_name(self.scheduler_cls, aliases=aliases)(
Apr 01 19:05:48 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/kombu/utils/imports.py", line 59, in symbol_by_name
Apr 01 19:05:48 [celery-beat]     module = imp(module_name, package=package, **kwargs)
Apr 01 19:05:48 [celery-beat]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
Apr 01 19:05:48 [celery-beat]     return _bootstrap._gcd_import(name[level:], package, level)
Apr 01 19:05:48 [celery-beat]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Apr 01 19:05:48 [celery-beat]   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
Apr 01 19:05:48 [celery-beat]   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
Apr 01 19:05:48 [celery-beat]   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
Apr 01 19:05:48 [celery-beat]   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
Apr 01 19:05:48 [celery-beat]   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
Apr 01 19:05:48 [celery-beat]   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/schedulers.py", line 19, in <module>
Apr 01 19:05:48 [celery-beat]     from .models import (ClockedSchedule, CrontabSchedule, IntervalSchedule,
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django_celery_beat/models.py", line 78, in <module>
Apr 01 19:05:48 [celery-beat]     class SolarSchedule(models.Model):
Apr 01 19:05:48 [celery-beat]   File "/usr/local/lib/python3.11/site-packages/django/db/models/base.py", line 134, in __new__
Apr 01 19:05:48 [celery-beat]     raise RuntimeError(
Apr 01 19:05:48 [celery-beat] RuntimeError: Model class django_celery_beat.models.SolarSchedule doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.