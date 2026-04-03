Apr 03 17:20:20  [34m╭────────────[34m[30m[44m git repo clone [0m[0m[34m───────────╼[0m
Apr 03 17:20:20  [34m│[0m [34m › fetching app source code[0m
Apr 03 17:20:20  [34m│[0m => Selecting branch "develop"
Apr 03 17:20:21  [34m│[0m => Checking out commit "c8f12c38c841016c683a96c848b54e24f0447c2e"
Apr 03 17:20:21  [34m│[0m 
Apr 03 17:20:21  [34m│[0m [32m ✔ cloned repo to [35m/workspace[0m[0m
Apr 03 17:20:21  [34m╰────────────────────────────────────────╼[0m
Apr 03 17:20:21  
Apr 03 17:20:21  [34m › applying source directory [35mfrontend[0m[0m
Apr 03 17:20:21  [32m ✔ using workspace root [35m/workspace/frontend[0m[0m
Apr 03 17:20:21  
Apr 03 17:20:22  [34m › configuring build-time app environment variables:[0m
Apr 03 17:20:22       NEXT_PUBLIC_API_URL NEXT_PUBLIC_TENANT_DOMAIN NODE_ENV NPM_CONFIG_LEGACY_PEER_DEPS
Apr 03 17:20:22  
Apr 03 17:20:22  [34m╭────────────[34m[30m[44m buildpack detection [0m[0m[34m───────────╼[0m
Apr 03 17:20:22  [34m│[0m [34m › using Ubuntu 22.04 stack[0m
Apr 03 17:20:24  [34m│[0m Detected the following buildpacks suitable to build your app:
Apr 03 17:20:24  [34m│[0m 
Apr 03 17:20:24  [34m│[0m    digitalocean/nodejs-appdetect  v0.1.2    
Apr 03 17:20:24  [34m│[0m    heroku/nodejs                  v0.338.5  (Node.js)
Apr 03 17:20:24  [34m│[0m    digitalocean/procfile          v0.1.0    (Procfile)
Apr 03 17:20:24  [34m│[0m    digitalocean/custom            v0.2.0    (Custom Build Command)
Apr 03 17:20:24  [34m╰─────────────────────────────────────────────╼[0m
Apr 03 17:20:24  
Apr 03 17:20:24  [34m╭────────────[34m[30m[44m app build [0m[0m[34m───────────╼[0m
Apr 03 17:20:24  [34m│[0m [33;1mWarning: [0mno analyzed metadata found at path '/layers/analyzed.toml'
Apr 03 17:20:24  [34m│[0m Timer: Builder started at 2026-04-03T17:20:24Z
Apr 03 17:20:24  [34m│[0m        
Apr 03 17:20:24  [34m│[0m -----> Creating runtime environment
Apr 03 17:20:25  [34m│[0m        
Apr 03 17:20:25  [34m│[0m        NPM_CONFIG_LOGLEVEL=error
Apr 03 17:20:25  [34m│[0m        NPM_CONFIG_LEGACY_PEER_DEPS=true
Apr 03 17:20:25  [34m│[0m        NODE_VERBOSE=false
Apr 03 17:20:25  [34m│[0m        NODE_ENV=production
Apr 03 17:20:25  [34m│[0m        NODE_MODULES_CACHE=true
Apr 03 17:20:25  [34m│[0m        
Apr 03 17:20:25  [34m│[0m -----> Installing binaries
Apr 03 17:20:25  [34m│[0m        engines.node (package.json):   unspecified
Apr 03 17:20:25  [34m│[0m        engines.npm (package.json):    unspecified (use default)
Apr 03 17:20:25  [34m│[0m        
Apr 03 17:20:25  [34m│[0m        Resolving node version 22.x...
Apr 03 17:20:25  [34m│[0m        Downloading and installing node 22.22.1...
Apr 03 17:20:26  [34m│[0m        Validating checksum
Apr 03 17:20:29  [34m│[0m        Using default npm version: 10.9.4
Apr 03 17:20:29  [34m│[0m        
Apr 03 17:20:29  [34m│[0m -----> Installing dependencies
Apr 03 17:20:29  [34m│[0m        Installing node modules
Apr 03 17:20:37  [34m│[0m        npm error code EUSAGE
Apr 03 17:20:37  [34m│[0m        npm error
Apr 03 17:20:37  [34m│[0m        npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
Apr 03 17:20:37  [34m│[0m        npm error
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's eslint-config-next@16.1.6 does not satisfy eslint-config-next@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's next@16.1.6 does not satisfy next@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/eslint-plugin-next@16.1.6 does not satisfy @next/eslint-plugin-next@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Missing: @rushstack/eslint-patch@1.16.1 from lock file
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/eslint-plugin@8.57.0 does not satisfy @typescript-eslint/eslint-plugin@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/parser@8.57.0 does not satisfy @typescript-eslint/parser@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's eslint-plugin-react-hooks@7.0.1 does not satisfy eslint-plugin-react-hooks@5.2.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/scope-manager@8.57.0 does not satisfy @typescript-eslint/scope-manager@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/type-utils@8.57.0 does not satisfy @typescript-eslint/type-utils@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/utils@8.57.0 does not satisfy @typescript-eslint/utils@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/visitor-keys@8.57.0 does not satisfy @typescript-eslint/visitor-keys@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's ts-api-utils@2.4.0 does not satisfy ts-api-utils@2.5.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/types@8.57.0 does not satisfy @typescript-eslint/types@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/typescript-estree@8.57.0 does not satisfy @typescript-eslint/typescript-estree@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/project-service@8.57.0 does not satisfy @typescript-eslint/project-service@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @typescript-eslint/tsconfig-utils@8.57.0 does not satisfy @typescript-eslint/tsconfig-utils@8.58.0
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's minimatch@10.2.4 does not satisfy minimatch@10.2.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/env@16.1.6 does not satisfy @next/env@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/swc-darwin-arm64@16.1.6 does not satisfy @next/swc-darwin-arm64@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/swc-darwin-x64@16.1.6 does not satisfy @next/swc-darwin-x64@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/swc-linux-arm64-gnu@16.1.6 does not satisfy @next/swc-linux-arm64-gnu@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/swc-linux-arm64-musl@16.1.6 does not satisfy @next/swc-linux-arm64-musl@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/swc-linux-x64-gnu@16.1.6 does not satisfy @next/swc-linux-x64-gnu@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/swc-linux-x64-musl@16.1.6 does not satisfy @next/swc-linux-x64-musl@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/swc-win32-arm64-msvc@16.1.6 does not satisfy @next/swc-win32-arm64-msvc@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @next/swc-win32-x64-msvc@16.1.6 does not satisfy @next/swc-win32-x64-msvc@15.1.6
Apr 03 17:20:37  [34m│[0m        npm error Missing: @swc/counter@0.1.3 from lock file
Apr 03 17:20:37  [34m│[0m        npm error Missing: busboy@1.6.0 from lock file
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's sharp@0.34.5 does not satisfy sharp@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Missing: streamsearch@1.1.0 from lock file
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-darwin-arm64@0.34.5 does not satisfy @img/sharp-darwin-arm64@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-darwin-x64@0.34.5 does not satisfy @img/sharp-darwin-x64@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-libvips-darwin-arm64@1.2.4 does not satisfy @img/sharp-libvips-darwin-arm64@1.0.4
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-libvips-darwin-x64@1.2.4 does not satisfy @img/sharp-libvips-darwin-x64@1.0.4
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-libvips-linux-arm@1.2.4 does not satisfy @img/sharp-libvips-linux-arm@1.0.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-libvips-linux-arm64@1.2.4 does not satisfy @img/sharp-libvips-linux-arm64@1.0.4
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-libvips-linux-s390x@1.2.4 does not satisfy @img/sharp-libvips-linux-s390x@1.0.4
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-libvips-linux-x64@1.2.4 does not satisfy @img/sharp-libvips-linux-x64@1.0.4
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-libvips-linuxmusl-arm64@1.2.4 does not satisfy @img/sharp-libvips-linuxmusl-arm64@1.0.4
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-libvips-linuxmusl-x64@1.2.4 does not satisfy @img/sharp-libvips-linuxmusl-x64@1.0.4
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-linux-arm@0.34.5 does not satisfy @img/sharp-linux-arm@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-linux-arm64@0.34.5 does not satisfy @img/sharp-linux-arm64@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-linux-s390x@0.34.5 does not satisfy @img/sharp-linux-s390x@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-linux-x64@0.34.5 does not satisfy @img/sharp-linux-x64@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-linuxmusl-arm64@0.34.5 does not satisfy @img/sharp-linuxmusl-arm64@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-linuxmusl-x64@0.34.5 does not satisfy @img/sharp-linuxmusl-x64@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-wasm32@0.34.5 does not satisfy @img/sharp-wasm32@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-win32-ia32@0.34.5 does not satisfy @img/sharp-win32-ia32@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's @img/sharp-win32-x64@0.34.5 does not satisfy @img/sharp-win32-x64@0.33.5
Apr 03 17:20:37  [34m│[0m        npm error Invalid: lock file's brace-expansion@5.0.4 does not satisfy brace-expansion@5.0.5
Apr 03 17:20:37  [34m│[0m        npm error
Apr 03 17:20:37  [34m│[0m        npm error Clean install a project
Apr 03 17:20:37  [34m│[0m        npm error
Apr 03 17:20:37  [34m│[0m        npm error Usage:
Apr 03 17:20:37  [34m│[0m        npm error npm ci
Apr 03 17:20:37  [34m│[0m        npm error
Apr 03 17:20:37  [34m│[0m        npm error Options:
Apr 03 17:20:37  [34m│[0m        npm error [--install-strategy <hoisted|nested|shallow|linked>] [--legacy-bundling]
Apr 03 17:20:37  [34m│[0m        npm error [--global-style] [--omit <dev|optional|peer> [--omit <dev|optional|peer> ...]]
Apr 03 17:20:37  [34m│[0m        npm error [--include <prod|dev|optional|peer> [--include <prod|dev|optional|peer> ...]]
Apr 03 17:20:37  [34m│[0m        npm error [--strict-peer-deps] [--foreground-scripts] [--ignore-scripts] [--no-audit]
Apr 03 17:20:37  [34m│[0m        npm error [--no-bin-links] [--no-fund] [--dry-run]
Apr 03 17:20:37  [34m│[0m        npm error [-w|--workspace <workspace-name> [-w|--workspace <workspace-name> ...]]
Apr 03 17:20:37  [34m│[0m        npm error [-ws|--workspaces] [--include-workspace-root] [--install-links]
Apr 03 17:20:37  [34m│[0m        npm error
Apr 03 17:20:37  [34m│[0m        npm error aliases: clean-install, ic, install-clean, isntall-clean
Apr 03 17:20:37  [34m│[0m        npm error
Apr 03 17:20:37  [34m│[0m        npm error Run "npm help ci" for more info
Apr 03 17:20:37  [34m│[0m        npm notice
Apr 03 17:20:37  [34m│[0m        npm notice New major version of npm available! 10.9.4 -> 11.12.1
Apr 03 17:20:37  [34m│[0m        npm notice Changelog: https://github.com/npm/cli/releases/tag/v11.12.1
Apr 03 17:20:37  [34m│[0m        npm notice To update run: npm install -g npm@11.12.1
Apr 03 17:20:37  [34m│[0m        npm notice
Apr 03 17:20:37  [34m│[0m        npm error A complete log of this run can be found in: /tmp/npmcache.zU2fp/_logs/2026-04-03T17_20_30_030Z-debug-0.log
Apr 03 17:20:37  [34m│[0m 
Apr 03 17:20:37  [34m│[0m -----> Build failed
Apr 03 17:20:38  [34m│[0m  !     npm lockfile is not in sync
Apr 03 17:20:38  [34m│[0m 
Apr 03 17:20:38  [34m│[0m        This error occurs when the contents of `package.json` contains a different
Apr 03 17:20:38  [34m│[0m        set of dependencies that the contents of `package-lock.json`. This can happen
Apr 03 17:20:38  [34m│[0m        when a package is added, modified, or removed but the lockfile was not updated.
Apr 03 17:20:38  [34m│[0m 
Apr 03 17:20:38  [34m│[0m        To fix this, run `npm install` locally in your app directory to regenerate the
Apr 03 17:20:38  [34m│[0m        lockfile, commit the changes to `package-lock.json`, and redeploy.
Apr 03 17:20:38  [34m│[0m       
Apr 03 17:20:38  [34m│[0m        https://devcenter.heroku.com/articles/troubleshooting-node-deploys#make-sure-that-the-lockfile-is-up-to-date
Apr 03 17:20:38  [34m│[0m 
Apr 03 17:20:38  [34m│[0m Timer: Builder ran for 13.832713972s and ended at 2026-04-03T17:20:38Z
Apr 03 17:20:38  [34m│[0m [31;1mERROR: [0mfailed to build: exit status 1
Apr 03 17:20:38  [34m│[0m 
Apr 03 17:20:38  [34m│[0m 
Apr 03 17:20:38  [34m│[0m [31m ✘ build failed[0m