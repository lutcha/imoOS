Apr 03 17:13:44  [34m╭────────────[34m[30m[44m git repo clone [0m[0m[34m───────────╼[0m
Apr 03 17:13:44  [34m│[0m [34m › fetching app source code[0m
Apr 03 17:13:44  [34m│[0m => Selecting branch "develop"
Apr 03 17:13:46  [34m│[0m => Checking out commit "b8585249eb239d71542e3f5aed7f28a8eecd382a"
Apr 03 17:13:47  [34m│[0m 
Apr 03 17:13:47  [34m│[0m [32m ✔ cloned repo to [35m/workspace[0m[0m
Apr 03 17:13:47  [34m╰────────────────────────────────────────╼[0m
Apr 03 17:13:47  
Apr 03 17:13:47  [34m › applying source directory [35mfrontend[0m[0m
Apr 03 17:13:47  [32m ✔ using workspace root [35m/workspace/frontend[0m[0m
Apr 03 17:13:47  
Apr 03 17:13:47  [34m › configuring build-time app environment variables:[0m
Apr 03 17:13:47       NEXT_PUBLIC_API_URL NEXT_PUBLIC_TENANT_DOMAIN NODE_ENV NPM_CONFIG_LEGACY_PEER_DEPS
Apr 03 17:13:47  
Apr 03 17:13:47  [34m╭────────────[34m[30m[44m buildpack detection [0m[0m[34m───────────╼[0m
Apr 03 17:13:47  [34m│[0m [34m › using Ubuntu 22.04 stack[0m
Apr 03 17:13:49  [34m│[0m Detected the following buildpacks suitable to build your app:
Apr 03 17:13:49  [34m│[0m 
Apr 03 17:13:49  [34m│[0m    digitalocean/nodejs-appdetect  v0.1.2    
Apr 03 17:13:49  [34m│[0m    heroku/nodejs                  v0.338.5  (Node.js)
Apr 03 17:13:49  [34m│[0m    digitalocean/procfile          v0.1.0    (Procfile)
Apr 03 17:13:49  [34m│[0m    digitalocean/custom            v0.2.0    (Custom Build Command)
Apr 03 17:13:49  [34m╰─────────────────────────────────────────────╼[0m
Apr 03 17:13:49  
Apr 03 17:13:49  [34m╭────────────[34m[30m[44m app build [0m[0m[34m───────────╼[0m
Apr 03 17:13:49  [34m│[0m [33;1mWarning: [0mno analyzed metadata found at path '/layers/analyzed.toml'
Apr 03 17:13:49  [34m│[0m Timer: Builder started at 2026-04-03T17:13:49Z
Apr 03 17:13:49  [34m│[0m        
Apr 03 17:13:49  [34m│[0m -----> Creating runtime environment
Apr 03 17:13:49  [34m│[0m        
Apr 03 17:13:49  [34m│[0m        NPM_CONFIG_LOGLEVEL=error
Apr 03 17:13:49  [34m│[0m        NPM_CONFIG_LEGACY_PEER_DEPS=true
Apr 03 17:13:49  [34m│[0m        NODE_VERBOSE=false
Apr 03 17:13:49  [34m│[0m        NODE_ENV=production
Apr 03 17:13:49  [34m│[0m        NODE_MODULES_CACHE=true
Apr 03 17:13:49  [34m│[0m        
Apr 03 17:13:49  [34m│[0m -----> Installing binaries
Apr 03 17:13:49  [34m│[0m        engines.node (package.json):   unspecified
Apr 03 17:13:49  [34m│[0m        engines.npm (package.json):    unspecified (use default)
Apr 03 17:13:49  [34m│[0m        
Apr 03 17:13:49  [34m│[0m        Resolving node version 22.x...
Apr 03 17:13:50  [34m│[0m        Downloading and installing node 22.22.1...
Apr 03 17:13:50  [34m│[0m        Validating checksum
Apr 03 17:13:53  [34m│[0m        Using default npm version: 10.9.4
Apr 03 17:13:53  [34m│[0m        
Apr 03 17:13:53  [34m│[0m -----> Installing dependencies
Apr 03 17:13:53  [34m│[0m        Installing node modules
Apr 03 17:14:16  [34m│[0m        
Apr 03 17:14:16  [34m│[0m        added 1042 packages, and audited 1043 packages in 23s
Apr 03 17:14:16  [34m│[0m        
Apr 03 17:14:16  [34m│[0m        290 packages are looking for funding
Apr 03 17:14:16  [34m│[0m          run `npm fund` for details
Apr 03 17:14:16  [34m│[0m        
Apr 03 17:14:16  [34m│[0m        11 vulnerabilities (6 low, 2 moderate, 3 high)
Apr 03 17:14:16  [34m│[0m        
Apr 03 17:14:16  [34m│[0m        To address issues that do not require attention, run:
Apr 03 17:14:16  [34m│[0m          npm audit fix
Apr 03 17:14:16  [34m│[0m        
Apr 03 17:14:16  [34m│[0m        To address all issues (including breaking changes), run:
Apr 03 17:14:16  [34m│[0m          npm audit fix --force
Apr 03 17:14:16  [34m│[0m        
Apr 03 17:14:16  [34m│[0m        Run `npm audit` for details.
Apr 03 17:14:16  [34m│[0m        npm notice
Apr 03 17:14:16  [34m│[0m        npm notice New major version of npm available! 10.9.4 -> 11.12.1
Apr 03 17:14:16  [34m│[0m        npm notice Changelog: https://github.com/npm/cli/releases/tag/v11.12.1
Apr 03 17:14:16  [34m│[0m        npm notice To update run: npm install -g npm@11.12.1
Apr 03 17:14:16  [34m│[0m        npm notice
Apr 03 17:14:16  [34m│[0m        
Apr 03 17:14:16  [34m│[0m -----> Build
Apr 03 17:14:16  [34m│[0m        Running build
Apr 03 17:14:16  [34m│[0m        
Apr 03 17:14:16  [34m│[0m        > frontend@0.1.0 build
Apr 03 17:14:16  [34m│[0m        > next build
Apr 03 17:14:16  [34m│[0m        
Apr 03 17:14:17  [34m│[0m        ⚠ Warning: Next.js inferred your workspace root, but it may not be correct.
Apr 03 17:14:17  [34m│[0m         We detected multiple lockfiles and selected the directory of /workspace/package-lock.json as the root directory.
Apr 03 17:14:17  [34m│[0m         To silence this warning, set `turbopack.root` in your Next.js config, or consider removing one of the lockfiles if it's not needed.
Apr 03 17:14:17  [34m│[0m           See https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack#root-directory for more information.
Apr 03 17:14:17  [34m│[0m         Detected additional lockfiles: 
Apr 03 17:14:17  [34m│[0m           * /workspace/frontend/package-lock.json
Apr 03 17:14:17  [34m│[0m        
Apr 03 17:14:17  [34m│[0m        ⚠ No build cache found. Please configure build caching for faster rebuilds. Read more: https://nextjs.org/docs/messages/no-cache
Apr 03 17:14:17  [34m│[0m        Attention: Next.js now collects completely anonymous telemetry regarding usage.
Apr 03 17:14:17  [34m│[0m        This information is used to shape Next.js' roadmap and prioritize features.
Apr 03 17:14:17  [34m│[0m        You can learn more, including how to opt-out if you'd not like to participate in this anonymous program, by visiting the following URL:
Apr 03 17:14:17  [34m│[0m        https://nextjs.org/telemetry
Apr 03 17:14:17  [34m│[0m        
Apr 03 17:14:17  [34m│[0m        ▲ Next.js 16.1.6 (Turbopack)
Apr 03 17:14:17  [34m│[0m        
Apr 03 17:14:17  [34m│[0m          Creating an optimized production build ...
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        > Build error occurred
Apr 03 17:14:27  [34m│[0m        Error: Turbopack build failed with 51 errors:
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/finance/page.tsx:13:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 11 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 13 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 14 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 15 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 16 |[39m [90m// ----- Types -----[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/investor/documents/page.tsx:4:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 2 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 3 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 4 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useAuth } [36mfrom[39m [32m"@/contexts/AuthContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m { [33mDownload[39m[33m,[39m [33mFileText[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/investor/documents/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/investor/documents/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/investor/documents/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/investor/documents/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/investor/page.tsx:4:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 2 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 3 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 4 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useAuth } [36mfrom[39m [32m"@/contexts/AuthContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m { [33mStatusBadge[39m } [36mfrom[39m [32m"@/components/ui/StatusBadge"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/investor/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/investor/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/investor/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/investor/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/settings/billing/page.tsx:4:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 2 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 3 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 4 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useAuth } [36mfrom[39m [32m"@/contexts/AuthContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m { [33mAlertTriangle[39m[33m,[39m [33mTrendingUp[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/billing/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/billing/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/billing/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/billing/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/crm/ReservationModal.tsx:6:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 4 |[39m [36mimport[39m { [33mX[39m[33m,[39m [33mLoader2[39m[33m,[39m [33mAlertCircle[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useUnits } [36mfrom[39m [32m"@/hooks/useUnits"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 6 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m { formatCve } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m [36mimport[39m type { [33mLead[39m } [36mfrom[39m [32m"@/hooks/useLeads"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 9 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/ReservationModal.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/ReservationModal.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/crm/UnitReservationModal.tsx:12:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 10 |[39m [36mimport[39m { [33mX[39m[33m,[39m [33mLoader2[39m[33m,[39m [33mAlertCircle[39m[33m,[39m [33mHome[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m [36mimport[39m { useQueryClient } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 12 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 13 |[39m [36mimport[39m { useLeads } [36mfrom[39m [32m"@/hooks/useLeads"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 14 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 15 |[39m [36mimport[39m { unitKeys[33m,[39m type [33mUnit[39m } [36mfrom[39m [32m"@/hooks/useUnits"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/UnitReservationModal.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/UnitReservationModal.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/layout/Sidebar.tsx:7:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m  5 |[39m [36mimport[39m { useAuth } [36mfrom[39m [32m"@/contexts/AuthContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  6 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  7 |[39m [36mimport[39m { getAccessToken } [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m  8 |[39m [36mimport[39m {
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m     [33mLayoutDashboard[39m[33m,[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m     [33mBuilding2[39m[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import trace:
Apr 03 17:14:27  [34m│[0m          Server Component:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/layout/Sidebar.tsx
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/layout.tsx
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/contexts/AuthContext.tsx:16:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 14 |[39m } [36mfrom[39m [32m"react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 15 |[39m [36mimport[39m { jwtDecode } [36mfrom[39m [32m"jwt-decode"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 16 |[39m [36mimport[39m { setAccessToken[33m,[39m setTenantSchema } [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 17 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 18 |[39m [36minterface[39m [33mJwtClaims[39m {
Apr 03 17:14:27  [34m│[0m         [90m 19 |[39m   user_id[33m:[39m string[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/contexts/AuthContext.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/superadmin/layout.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/superadmin/layout.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/contexts/AuthContext.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/superadmin/layout.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/superadmin/layout.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/useBuildings.ts:4:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 2 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 3 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 4 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mexport[39m [36minterface[39m [33mBuilding[39m {[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useBuildings.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useBuildings.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/useConstruction.ts:6:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 4 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useQuery[33m,[39m useMutation[33m,[39m useQueryClient } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 6 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 9 |[39m [90m// ----- Types -----[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useConstruction.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useConstruction.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/useContracts.ts:7:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m  5 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m         [90m  6 |[39m [36mimport[39m { useQuery[33m,[39m useMutation[33m,[39m useQueryClient } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  7 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m  8 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [90m// ----- Types -----[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useContracts.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useContracts.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/useDashboardStats.ts:7:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m  5 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m         [90m  6 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  7 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m  8 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [36mexport[39m [36minterface[39m [33mDashboardStats[39m {[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useDashboardStats.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useDashboardStats.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/useLeads.ts:7:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m  5 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m         [90m  6 |[39m [36mimport[39m { useQuery[33m,[39m useMutation[33m,[39m useQueryClient } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  7 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m  8 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [90m// ----- Types -----[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useLeads.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useLeads.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/useMarketplace.ts:6:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 4 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useQuery[33m,[39m useMutation[33m,[39m useQueryClient } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 6 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 9 |[39m [90m// ----- Types -----[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useMarketplace.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useMarketplace.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/usePaymentPlans.ts:6:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 4 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useQuery[33m,[39m useMutation[33m,[39m useQueryClient } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 6 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m [36mimport[39m { contractKeys } [36mfrom[39m [32m"@/hooks/useContracts"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 9 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/usePaymentPlans.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/usePaymentPlans.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/useProjects.ts:10:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m  8 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 10 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 13 |[39m [90m// ----- Types -----[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useProjects.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useProjects.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/useTenantSettings.ts:4:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m 2 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 3 |[39m [36mimport[39m { useQuery[33m,[39m useMutation[33m,[39m useQueryClient } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 4 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mexport[39m [36minterface[39m [33mTenantSettings[39m {[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useTenantSettings.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useTenantSettings.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/hooks/useUnits.ts:7:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/api-client'
Apr 03 17:14:27  [34m│[0m        [0m [90m  5 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m         [90m  6 |[39m [36mimport[39m { useQuery[33m,[39m useMutation[33m,[39m useQueryClient } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  7 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m  8 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [90m// ----- Types -----[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/api-client' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useUnits.ts [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/hooks/useUnits.ts [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/construction/page.tsx:26:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m 24 |[39m [36mimport[39m { useBuildings } [36mfrom[39m [32m"@/hooks/useBuildings"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 25 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 26 |[39m [36mimport[39m { formatDate } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 27 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 28 |[39m [90m// ----- Status config -----[39m
Apr 03 17:14:27  [34m│[0m         [90m 29 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/contracts/[id]/page.tsx:23:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m 21 |[39m } [36mfrom[39m [32m"@/hooks/usePaymentPlans"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 22 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 23 |[39m [36mimport[39m { formatDate[33m,[39m formatCve } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 24 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 25 |[39m [90m// ----- Contract status badge -----[39m
Apr 03 17:14:27  [34m│[0m         [90m 26 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/contracts/page.tsx:8:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m  6 |[39m [36mimport[39m { useContracts[33m,[39m type [33mContractStatus[39m } [36mfrom[39m [32m"@/hooks/useContracts"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  7 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  8 |[39m [36mimport[39m { formatDate[33m,[39m formatCve } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [90m// ----- Status config -----[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/crm/page.tsx:13:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m 11 |[39m [36mimport[39m { [33mLeadStatusBadge[39m } [36mfrom[39m [32m"@/components/ui/StatusBadge"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 13 |[39m [36mimport[39m { formatDate } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 14 |[39m [36mimport[39m { [33mKanbanBoard[39m } [36mfrom[39m [32m"@/components/crm/KanbanBoard"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 15 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 16 |[39m [36mexport[39m [36mdefault[39m [36mfunction[39m [33mCrmPage[39m() {[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/finance/page.tsx:10:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m  8 |[39m [36mimport[39m { [33mWallet[39m[33m,[39m [33mSearch[39m[33m,[39m [33mCheckCircle2[39m[33m,[39m [33mClock[39m[33m,[39m [33mAlertCircle[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 10 |[39m [36mimport[39m { formatCve[33m,[39m formatDate } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 13 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/inventory/page.tsx:15:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m 13 |[39m [36mimport[39m { [33mUnitStatusBadge[39m } [36mfrom[39m [32m"@/components/ui/StatusBadge"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 14 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 15 |[39m [36mimport[39m { formatArea[33m,[39m formatCve[33m,[39m formatEur } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 16 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 17 |[39m [36mconst[39m [33mPAGE_SIZE[39m [33m=[39m [35m20[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 18 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/marketplace/page.tsx:9:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m  7 |[39m [36mimport[39m { [33mAlertTriangle[39m[33m,[39m [33mRefreshCw[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  8 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  9 |[39m [36mimport[39m { formatCve[33m,[39m formatDateTime } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m [36mimport[39m {
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m   useMarketplaceListings[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/projects/[id]/page.tsx:12:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m 10 |[39m [36mimport[39m { [33mProjectStatusBadge[39m[33m,[39m [33mUnitStatusBadge[39m } [36mfrom[39m [32m"@/components/ui/StatusBadge"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 12 |[39m [36mimport[39m { formatDate[33m,[39m formatArea[33m,[39m formatCve[33m,[39m formatEur } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 13 |[39m [36mimport[39m { [33mUnitReservationModal[39m } [36mfrom[39m [32m"@/components/crm/UnitReservationModal"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 14 |[39m [36mimport[39m type { [33mUnit[39m } [36mfrom[39m [32m"@/hooks/useUnits"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 15 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/projects/page.tsx:10:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m  8 |[39m [36mimport[39m { [33mProjectStatusBadge[39m } [36mfrom[39m [32m"@/components/ui/StatusBadge"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 10 |[39m [36mimport[39m { formatDate } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m [36mconst[39m [33mSTATUS_OPTIONS[39m[33m:[39m { value[33m:[39m [33mProjectStatus[39m [33m|[39m [32m""[39m[33m;[39m label[33m:[39m string }[] [33m=[39m [
Apr 03 17:14:27  [34m│[0m         [90m 13 |[39m   { value[33m:[39m [32m""[39m[33m,[39m             label[33m:[39m [32m"Todos os estados"[39m }[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/crm/LeadCard.tsx:8:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m  6 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  7 |[39m [36mimport[39m type { [33mLead[39m } [36mfrom[39m [32m"@/hooks/useLeads"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  8 |[39m [36mimport[39m { formatCve } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [36minterface[39m [33mLeadCardProps[39m {
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m     lead[33m:[39m [33mLead[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/LeadCard.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/LeadCard.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/crm/ReservationModal.tsx:7:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m  5 |[39m [36mimport[39m { useUnits } [36mfrom[39m [32m"@/hooks/useUnits"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  6 |[39m [36mimport[39m apiClient [36mfrom[39m [32m"@/lib/api-client"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  7 |[39m [36mimport[39m { formatCve } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m  8 |[39m [36mimport[39m type { [33mLead[39m } [36mfrom[39m [32m"@/hooks/useLeads"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [36minterface[39m [33mReservationModalProps[39m {[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/ReservationModal.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/ReservationModal.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/crm/UnitReservationModal.tsx:16:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/format'
Apr 03 17:14:27  [34m│[0m        [0m [90m 14 |[39m [36mimport[39m { useTenant } [36mfrom[39m [32m"@/contexts/TenantContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 15 |[39m [36mimport[39m { unitKeys[33m,[39m type [33mUnit[39m } [36mfrom[39m [32m"@/hooks/useUnits"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 16 |[39m [36mimport[39m { formatCve[33m,[39m formatArea } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 17 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 18 |[39m [36minterface[39m [33mUnitReservationModalProps[39m {
Apr 03 17:14:27  [34m│[0m         [90m 19 |[39m   unit[33m:[39m [33mUnit[39m [33m|[39m [36mnull[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/format' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/UnitReservationModal.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/UnitReservationModal.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/construction/page.tsx:15:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 13 |[39m   [33mX[39m[33m,[39m
Apr 03 17:14:27  [34m│[0m         [90m 14 |[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 15 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 16 |[39m [36mimport[39m {
Apr 03 17:14:27  [34m│[0m         [90m 17 |[39m   useDailyReports[33m,[39m
Apr 03 17:14:27  [34m│[0m         [90m 18 |[39m   useCreateDailyReport[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/construction/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/contracts/[id]/page.tsx:13:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 11 |[39m   [33mAlertCircle[39m[33m,[39m
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 13 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 14 |[39m [36mimport[39m { useContract[33m,[39m type [33mContractStatus[39m } [36mfrom[39m [32m"@/hooks/useContracts"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 15 |[39m [36mimport[39m {
Apr 03 17:14:27  [34m│[0m         [90m 16 |[39m   useGeneratePaymentPlan[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/contracts/page.tsx:5:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 3 |[39m [36mimport[39m { useState } [36mfrom[39m [32m"react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 4 |[39m [36mimport[39m { [33mFileText[39m[33m,[39m [33mSearch[39m[33m,[39m [33mFileCheck2[39m[33m,[39m [33mClock[39m[33m,[39m [33mBan[39m[33m,[39m [33mCheckCircle2[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 5 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m [36mimport[39m { useContracts[33m,[39m type [33mContractStatus[39m } [36mfrom[39m [32m"@/hooks/useContracts"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m [36mimport[39m { formatDate[33m,[39m formatCve } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/contracts/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/crm/page.tsx:9:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m  7 |[39m [36mimport[39m { [33mSearch[39m[33m,[39m [33mUsers2[39m[33m,[39m [33mLayoutList[39m[33m,[39m [33mLayoutGrid[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  8 |[39m [36mimport[39m { useState } [36mfrom[39m [32m"react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  9 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [36mimport[39m { useLeads } [36mfrom[39m [32m"@/hooks/useLeads"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m [36mimport[39m { [33mLeadStatusBadge[39m } [36mfrom[39m [32m"@/components/ui/StatusBadge"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/finance/page.tsx:9:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m  7 |[39m [36mimport[39m { useState } [36mfrom[39m [32m"react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m  8 |[39m [36mimport[39m { [33mWallet[39m[33m,[39m [33mSearch[39m[33m,[39m [33mCheckCircle2[39m[33m,[39m [33mClock[39m[33m,[39m [33mAlertCircle[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  9 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [36mimport[39m { formatCve[33m,[39m formatDate } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m [36mimport[39m { useQuery } [36mfrom[39m [32m"@tanstack/react-query"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/finance/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/inventory/page.tsx:11:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m  9 |[39m [36mimport[39m { useState[33m,[39m useCallback } [36mfrom[39m [32m"react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [36mimport[39m { [33mSearch[39m[33m,[39m [33mSlidersHorizontal[39m[33m,[39m [33mChevronLeft[39m[33m,[39m [33mChevronRight[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 11 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 12 |[39m [36mimport[39m { useUnits[33m,[39m type [33mUnitStatus[39m } [36mfrom[39m [32m"@/hooks/useUnits"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 13 |[39m [36mimport[39m { [33mUnitStatusBadge[39m } [36mfrom[39m [32m"@/components/ui/StatusBadge"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 14 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/inventory/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/marketplace/page.tsx:8:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m  6 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m         [90m  7 |[39m [36mimport[39m { [33mAlertTriangle[39m[33m,[39m [33mRefreshCw[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m  8 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m  9 |[39m [36mimport[39m { formatCve[33m,[39m formatDateTime } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 10 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 11 |[39m [36mimport[39m {[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/marketplace/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/page.tsx:15:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 13 |[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 14 |[39m [36mimport[39m [33mLink[39m [36mfrom[39m [32m"next/link"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 15 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 16 |[39m [36mimport[39m { useAuth } [36mfrom[39m [32m"@/contexts/AuthContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 17 |[39m [36mimport[39m { useDashboardStats[33m,[39m activeLeadsCount } [36mfrom[39m [32m"@/hooks/useDashboardStats"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 18 |[39m [36mimport[39m { useProjects[33m,[39m featureToProject } [36mfrom[39m [32m"@/hooks/useProjects"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/projects/[id]/page.tsx:6:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 4 |[39m [36mimport[39m { useParams[33m,[39m useRouter } [36mfrom[39m [32m"next/navigation"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { [33mArrowLeft[39m[33m,[39m [33mBuilding2[39m[33m,[39m [33mMapPin[39m[33m,[39m [33mCalendarClock[39m[33m,[39m [33mLayers[39m[33m,[39m [33mBuilding[39m[33m,[39m [33mBookmarkPlus[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 6 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m { useProject[33m,[39m featureToProject } [36mfrom[39m [32m"@/hooks/useProjects"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m [36mimport[39m { useUnits } [36mfrom[39m [32m"@/hooks/useUnits"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 9 |[39m [36mimport[39m { useBuildings } [36mfrom[39m [32m"@/hooks/useBuildings"[39m[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/projects/[id]/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/app/settings/page.tsx:14:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 12 |[39m     [33mAlertCircle[39m
Apr 03 17:14:27  [34m│[0m         [90m 13 |[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 14 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 15 |[39m [36mimport[39m { useTenantSettings[33m,[39m useUpdateTenantSettings } [36mfrom[39m [32m"@/hooks/useTenantSettings"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 16 |[39m [36mimport[39m { [33mSkeleton[39m } [36mfrom[39m [32m"@/components/ui/Skeleton"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 17 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/crm/KanbanColumn.tsx:4:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 2 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 3 |[39m [36mimport[39m { useDroppable } [36mfrom[39m [32m"@dnd-kit/core"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 4 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m type { [33mLead[39m[33m,[39m [33mLeadStatus[39m[33m,[39m [33mPipelineColumn[39m } [36mfrom[39m [32m"@/hooks/useLeads"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m [36mimport[39m { [33mLeadCard[39m } [36mfrom[39m [32m"./LeadCard"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanColumn.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanColumn.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/crm/LeadCard.tsx:6:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 4 |[39m [36mimport[39m { [33mCSS[39m } [36mfrom[39m [32m"@dnd-kit/utilities"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { [33mMoreHorizontal[39m[33m,[39m [33mCalendar[39m[33m,[39m [33mCreditCard[39m[33m,[39m [33mBuilding[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 6 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m type { [33mLead[39m } [36mfrom[39m [32m"@/hooks/useLeads"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m [36mimport[39m { formatCve } [36mfrom[39m [32m"@/lib/format"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 9 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/LeadCard.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/LeadCard.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/crm/KanbanBoard.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/layout/Sidebar.tsx:22:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 20 |[39m     [33mStore[39m[33m,[39m
Apr 03 17:14:27  [34m│[0m         [90m 21 |[39m } [36mfrom[39m [32m"lucide-react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 22 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m    |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 23 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 24 |[39m [36minterface[39m [33mUsageData[39m {
Apr 03 17:14:27  [34m│[0m         [90m 25 |[39m   plan[33m:[39m string[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import trace:
Apr 03 17:14:27  [34m│[0m          Server Component:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/layout/Sidebar.tsx
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/layout.tsx
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/layout/Topbar.tsx:6:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 4 |[39m [36mimport[39m { useAuth } [36mfrom[39m [32m"@/contexts/AuthContext"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mimport[39m { useState } [36mfrom[39m [32m"react"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 6 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m [36mexport[39m [36mfunction[39m [33mTopbar[39m() {
Apr 03 17:14:27  [34m│[0m         [90m 9 |[39m     [36mconst[39m { user[33m,[39m tenant[33m,[39m logout } [33m=[39m useAuth()[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import trace:
Apr 03 17:14:27  [34m│[0m          Server Component:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/layout/Topbar.tsx
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/layout.tsx
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/ui/Skeleton.tsx:6:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 4 |[39m [90m * Skill: tailwind-design-tokens[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 6 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m [36minterface[39m [33mSkeletonProps[39m {
Apr 03 17:14:27  [34m│[0m         [90m 9 |[39m   className[33m?[39m[33m:[39m string[33m;[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/Skeleton.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/billing/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/billing/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/Skeleton.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/billing/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/billing/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/ui/StatusBadge.tsx:6:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 4 |[39m [90m * Skill: unit-status-workflow, tailwind-design-tokens[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [90m */[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 6 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m [36mimport[39m type { [33mUnitStatus[39m } [36mfrom[39m [32m"@/hooks/useUnits"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 8 |[39m [36mimport[39m type { [33mProjectStatus[39m } [36mfrom[39m [32m"@/hooks/useProjects"[39m[33m;[39m
Apr 03 17:14:27  [34m│[0m         [90m 9 |[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/StatusBadge.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/StatusBadge.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/crm/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/ui/alert.tsx:3:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 1 |[39m [36mimport[39m [33m*[39m [36mas[39m [33mReact[39m [36mfrom[39m [32m"react"[39m
Apr 03 17:14:27  [34m│[0m         [90m 2 |[39m [36mimport[39m { cva[33m,[39m type [33mVariantProps[39m } [36mfrom[39m [32m"class-variance-authority"[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 3 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 4 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mconst[39m alertVariants [33m=[39m cva(
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m   [32m"relative w-full rounded-lg border px-4 py-3 text-sm [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground [&>svg~*]:pl-7"[39m[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/alert.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/alert.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/ui/badge.tsx:3:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 1 |[39m [36mimport[39m [33m*[39m [36mas[39m [33mReact[39m [36mfrom[39m [32m"react"[39m
Apr 03 17:14:27  [34m│[0m         [90m 2 |[39m [36mimport[39m { cva[33m,[39m type [33mVariantProps[39m } [36mfrom[39m [32m"class-variance-authority"[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 3 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 4 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m [36mconst[39m badgeVariants [33m=[39m cva(
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m   [32m"inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"[39m[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/badge.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/badge.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/ui/button.tsx:4:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 2 |[39m [36mimport[39m { [33mSlot[39m } [36mfrom[39m [32m"@radix-ui/react-slot"[39m
Apr 03 17:14:27  [34m│[0m         [90m 3 |[39m [36mimport[39m { cva[33m,[39m type [33mVariantProps[39m } [36mfrom[39m [32m"class-variance-authority"[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 4 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 6 |[39m [36mconst[39m buttonVariants [33m=[39m cva(
Apr 03 17:14:27  [34m│[0m         [90m 7 |[39m   [32m"inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0"[39m[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/button.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/button.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/ui/card.tsx:2:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 1 |[39m [36mimport[39m [33m*[39m [36mas[39m [33mReact[39m [36mfrom[39m [32m"react"[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 2 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 3 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 4 |[39m [36mconst[39m [33mCard[39m [33m=[39m [33mReact[39m[33m.[39mforwardRef[33m<[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m   [33mHTMLDivElement[39m[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/card.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/card.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        ./frontend/src/components/ui/table.tsx:2:1
Apr 03 17:14:27  [34m│[0m        Module not found: Can't resolve '@/lib/utils'
Apr 03 17:14:27  [34m│[0m        [0m [90m 1 |[39m [36mimport[39m [33m*[39m [36mas[39m [33mReact[39m [36mfrom[39m [32m"react"[39m
Apr 03 17:14:27  [34m│[0m        [31m[1m>[22m[39m[90m 2 |[39m [36mimport[39m { cn } [36mfrom[39m [32m"@/lib/utils"[39m
Apr 03 17:14:27  [34m│[0m         [90m   |[39m [31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m[31m[1m^[22m[39m
Apr 03 17:14:27  [34m│[0m         [90m 3 |[39m
Apr 03 17:14:27  [34m│[0m         [90m 4 |[39m [36mconst[39m [33mTable[39m [33m=[39m [33mReact[39m[33m.[39mforwardRef[33m<[39m
Apr 03 17:14:27  [34m│[0m         [90m 5 |[39m   [33mHTMLTableElement[39m[33m,[39m[0m
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import map: aliased to relative './src/lib/utils' inside of [project]/frontend
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Import traces:
Apr 03 17:14:27  [34m│[0m          Client Component Browser:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/table.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component Browser]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m          Client Component SSR:
Apr 03 17:14:27  [34m│[0m            ./frontend/src/components/ui/table.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Client Component SSR]
Apr 03 17:14:27  [34m│[0m            ./frontend/src/app/settings/whatsapp/page.tsx [Server Component]
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        https://nextjs.org/docs/messages/module-not-found
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/finance/page.tsx:13:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/investor/documents/page.tsx:4:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/investor/page.tsx:4:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/settings/billing/page.tsx:4:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/crm/ReservationModal.tsx:6:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/crm/UnitReservationModal.tsx:12:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/layout/Sidebar.tsx:7:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/contexts/AuthContext.tsx:16:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/useBuildings.ts:4:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/useConstruction.ts:6:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/useContracts.ts:7:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/useDashboardStats.ts:7:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/useLeads.ts:7:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/useMarketplace.ts:6:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/usePaymentPlans.ts:6:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/useProjects.ts:10:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/useTenantSettings.ts:4:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/hooks/useUnits.ts:7:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/construction/page.tsx:26:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/contracts/[id]/page.tsx:23:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/contracts/page.tsx:8:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/crm/page.tsx:13:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/finance/page.tsx:10:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/inventory/page.tsx:15:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/marketplace/page.tsx:9:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/projects/[id]/page.tsx:12:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/projects/page.tsx:10:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/crm/LeadCard.tsx:8:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/crm/ReservationModal.tsx:7:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/crm/UnitReservationModal.tsx:16:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/construction/page.tsx:15:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/contracts/[id]/page.tsx:13:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/contracts/page.tsx:5:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/crm/page.tsx:9:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/finance/page.tsx:9:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/inventory/page.tsx:11:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/marketplace/page.tsx:8:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/page.tsx:15:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/projects/[id]/page.tsx:6:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/app/settings/page.tsx:14:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/crm/KanbanColumn.tsx:4:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/crm/LeadCard.tsx:6:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/layout/Sidebar.tsx:22:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/layout/Topbar.tsx:6:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/ui/Skeleton.tsx:6:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/ui/StatusBadge.tsx:6:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/ui/alert.tsx:3:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/ui/badge.tsx:3:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/ui/button.tsx:4:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/ui/card.tsx:2:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m            at <unknown> (./frontend/src/components/ui/table.tsx:2:1)
Apr 03 17:14:27  [34m│[0m            at <unknown> (https://nextjs.org/docs/messages/module-not-found)
Apr 03 17:14:27  [34m│[0m 
Apr 03 17:14:27  [34m│[0m -----> Build failed
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        We're sorry this build is failing! You can troubleshoot common issues here:
Apr 03 17:14:27  [34m│[0m        https://devcenter.heroku.com/articles/troubleshooting-node-deploys
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Some possible problems:
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        - Node version not specified in package.json
Apr 03 17:14:27  [34m│[0m          https://devcenter.heroku.com/articles/nodejs-support#specifying-a-node-js-version
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m        Love,
Apr 03 17:14:27  [34m│[0m        Heroku
Apr 03 17:14:27  [34m│[0m        
Apr 03 17:14:27  [34m│[0m Timer: Builder ran for 38.807611506s and ended at 2026-04-03T17:14:27Z
Apr 03 17:14:27  [34m│[0m [31;1mERROR: [0mfailed to build: exit status 1
Apr 03 17:14:28  [34m│[0m 
Apr 03 17:14:28  [34m│[0m 
Apr 03 17:14:28  [34m│[0m [31m ✘ build failed[0m