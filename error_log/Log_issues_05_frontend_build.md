Apr 03 17:04:45  [34m╭────────────[34m[30m[44m git repo clone [0m[0m[34m───────────╼[0m
Apr 03 17:04:45  [34m│[0m [34m › fetching app source code[0m
Apr 03 17:04:45  [34m│[0m => Selecting branch "develop"
Apr 03 17:04:47  [34m│[0m => Checking out commit "da3ac604922e0ce40eedc255f7e78a192343c970"
Apr 03 17:04:47  [34m│[0m 
Apr 03 17:04:47  [34m│[0m [32m ✔ cloned repo to [35m/workspace[0m[0m
Apr 03 17:04:47  [34m╰────────────────────────────────────────╼[0m
Apr 03 17:04:47  
Apr 03 17:04:47  [34m › applying source directory [35mfrontend[0m[0m
Apr 03 17:04:47  [32m ✔ using workspace root [35m/workspace/frontend[0m[0m
Apr 03 17:04:47  
Apr 03 17:04:47  [34m › configuring build-time app environment variables:[0m
Apr 03 17:04:47       NODE_ENV NEXT_PUBLIC_API_URL NEXT_PUBLIC_TENANT_DOMAIN
Apr 03 17:04:47  
Apr 03 17:04:47  [34m╭────────────[34m[30m[44m buildpack detection [0m[0m[34m───────────╼[0m
Apr 03 17:04:47  [34m│[0m [34m › using Ubuntu 22.04 stack[0m
Apr 03 17:04:49  [34m│[0m Detected the following buildpacks suitable to build your app:
Apr 03 17:04:49  [34m│[0m 
Apr 03 17:04:49  [34m│[0m    digitalocean/nodejs-appdetect  v0.1.2    
Apr 03 17:04:49  [34m│[0m    heroku/nodejs                  v0.338.5  (Node.js)
Apr 03 17:04:49  [34m│[0m    digitalocean/procfile          v0.1.0    (Procfile)
Apr 03 17:04:49  [34m│[0m    digitalocean/custom            v0.2.0    (Custom Build Command)
Apr 03 17:04:49  [34m╰─────────────────────────────────────────────╼[0m
Apr 03 17:04:49  
Apr 03 17:04:49  [34m╭────────────[34m[30m[44m app build [0m[0m[34m───────────╼[0m
Apr 03 17:04:49  [34m│[0m [33;1mWarning: [0mno analyzed metadata found at path '/layers/analyzed.toml'
Apr 03 17:04:49  [34m│[0m Timer: Builder started at 2026-04-03T17:04:49Z
Apr 03 17:04:50  [34m│[0m        
Apr 03 17:04:50  [34m│[0m -----> Creating runtime environment
Apr 03 17:04:50  [34m│[0m        
Apr 03 17:04:50  [34m│[0m        NPM_CONFIG_LOGLEVEL=error
Apr 03 17:04:50  [34m│[0m        NODE_VERBOSE=false
Apr 03 17:04:50  [34m│[0m        NODE_ENV=production
Apr 03 17:04:50  [34m│[0m        NODE_MODULES_CACHE=true
Apr 03 17:04:50  [34m│[0m        
Apr 03 17:04:50  [34m│[0m -----> Installing binaries
Apr 03 17:04:50  [34m│[0m        engines.node (package.json):   unspecified
Apr 03 17:04:50  [34m│[0m        engines.npm (package.json):    unspecified (use default)
Apr 03 17:04:50  [34m│[0m        
Apr 03 17:04:50  [34m│[0m        Resolving node version 22.x...
Apr 03 17:04:50  [34m│[0m        Downloading and installing node 22.22.1...
Apr 03 17:04:51  [34m│[0m        Validating checksum
Apr 03 17:04:53  [34m│[0m        Using default npm version: 10.9.4
Apr 03 17:04:54  [34m│[0m        
Apr 03 17:04:54  [34m│[0m -----> Installing dependencies
Apr 03 17:04:54  [34m│[0m        Installing node modules
Apr 03 17:04:58  [34m│[0m        npm error code ERESOLVE
Apr 03 17:04:58  [34m│[0m        npm error ERESOLVE could not resolve
Apr 03 17:04:58  [34m│[0m        npm error
Apr 03 17:04:58  [34m│[0m        npm error While resolving: @storybook/nextjs@8.6.18
Apr 03 17:04:58  [34m│[0m        npm error Found: next@16.1.6
Apr 03 17:04:58  [34m│[0m        npm error node_modules/next
Apr 03 17:04:58  [34m│[0m        npm error   next@"16.1.6" from the root project
Apr 03 17:04:58  [34m│[0m        npm error
Apr 03 17:04:58  [34m│[0m        npm error Could not resolve dependency:
Apr 03 17:04:58  [34m│[0m        npm error peer next@"^13.5.0 || ^14.0.0 || ^15.0.0" from @storybook/nextjs@8.6.18
Apr 03 17:04:58  [34m│[0m        npm error node_modules/@storybook/nextjs
Apr 03 17:04:58  [34m│[0m        npm error   dev @storybook/nextjs@"^8.0.0" from the root project
Apr 03 17:04:58  [34m│[0m        npm error
Apr 03 17:04:58  [34m│[0m        npm error Conflicting peer dependency: next@15.5.14
Apr 03 17:04:58  [34m│[0m        npm error node_modules/next
Apr 03 17:04:58  [34m│[0m        npm error   peer next@"^13.5.0 || ^14.0.0 || ^15.0.0" from @storybook/nextjs@8.6.18
Apr 03 17:04:58  [34m│[0m        npm error   node_modules/@storybook/nextjs
Apr 03 17:04:58  [34m│[0m        npm error     dev @storybook/nextjs@"^8.0.0" from the root project
Apr 03 17:04:58  [34m│[0m        npm error
Apr 03 17:04:58  [34m│[0m        npm error Fix the upstream dependency conflict, or retry
Apr 03 17:04:58  [34m│[0m        npm error this command with --force or --legacy-peer-deps
Apr 03 17:04:58  [34m│[0m        npm error to accept an incorrect (and potentially broken) dependency resolution.
Apr 03 17:04:58  [34m│[0m        npm error
Apr 03 17:04:58  [34m│[0m        npm error
Apr 03 17:04:58  [34m│[0m        npm error For a full report see:
Apr 03 17:04:58  [34m│[0m        npm error /tmp/npmcache.HFU8t/_logs/2026-04-03T17_04_54_620Z-eresolve-report.txt
Apr 03 17:04:58  [34m│[0m        npm notice
Apr 03 17:04:58  [34m│[0m        npm notice New major version of npm available! 10.9.4 -> 11.12.1
Apr 03 17:04:58  [34m│[0m        npm notice Changelog: https://github.com/npm/cli/releases/tag/v11.12.1
Apr 03 17:04:58  [34m│[0m        npm notice To update run: npm install -g npm@11.12.1
Apr 03 17:04:58  [34m│[0m        npm notice
Apr 03 17:04:58  [34m│[0m        npm error A complete log of this run can be found in: /tmp/npmcache.HFU8t/_logs/2026-04-03T17_04_54_620Z-debug-0.log
Apr 03 17:04:58  [34m│[0m 
Apr 03 17:04:58  [34m│[0m -----> Build failed
Apr 03 17:04:58  [34m│[0m  !     Conflict detected in requested npm dependencies
Apr 03 17:04:58  [34m│[0m 
Apr 03 17:04:58  [34m│[0m        An `ERESOLVE` error during installation of npm dependencies means your app contains two or more conflicting
Apr 03 17:04:58  [34m│[0m        versions of the same dependency. This is typically caused by peer dependency requirements of requested dependencies.
Apr 03 17:04:58  [34m│[0m        The error above should contain more detail about which dependencies are in conflict. Use tools like `npm info <package-name>`
Apr 03 17:04:58  [34m│[0m        to get details about a package, including it's peer dependencies.
Apr 03 17:04:58  [34m│[0m 
Apr 03 17:04:58  [34m│[0m        The best way to address this issue is to regularly update your dependency versions to prevent conflicts from happening.
Apr 03 17:04:58  [34m│[0m 
Apr 03 17:04:58  [34m│[0m        If that is not possible, a temporary solution is to set a config var with `heroku set config npm_config_legacy_peer_deps=true`.
Apr 03 17:04:58  [34m│[0m        This should be used with caution as ignoring peer dependency conflicts can lead to unexpected runtime errors.
Apr 03 17:04:58  [34m│[0m     
Apr 03 17:04:58  [34m│[0m        https://devcenter.heroku.com/articles/nodejs-support
Apr 03 17:04:58  [34m│[0m 
Apr 03 17:04:58  [34m│[0m Timer: Builder ran for 8.610384493s and ended at 2026-04-03T17:04:58Z
Apr 03 17:04:58  [34m│[0m [31;1mERROR: [0mfailed to build: exit status 1
Apr 03 17:04:58  [34m│[0m 
Apr 03 17:04:58  [34m│[0m 
Apr 03 17:04:58  [34m│[0m [31m ✘ build failed[0m