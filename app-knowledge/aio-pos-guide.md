---
status: in-progress
owner: wahyu
updated: 2026-11-23
source-sha: 341775157
---

# aio-pos — App Guide

The single reference for **what the current POS app is and how it works**, written for every phase of
the Nuxt 2 → Nuxt 4 migration. It describes the app as found; it holds no recommendations.

- **Source:** `~/Work/aio-pos`, branch `master`, commit `341775157` (2026-11-17), Bitbucket
  `appliance-io/aio-pos`.
- **Citations:** `path:line` refers to `aio-pos` at the commit above.
- **Counts:** taken with `rg` over `.vue`/`.js` files, which respects `.gitignore`. The commands for
  the headline numbers are in [Appendix A](#appendix-a--how-to-re-measure). If you re-measure at a
  newer commit, update the number and the `source-sha`.
- **Code graph:** `graphify-out/` at the root of this repo (see [§17](#17-code-graph-graphify)).

## Contents

1. [At a glance](#1-at-a-glance)
2. [Stack and versions](#2-stack-and-versions)
3. [Repository layout](#3-repository-layout)
4. [Business domains](#4-business-domains)
5. [Routing and pages](#5-routing-and-pages)
6. [Layouts](#6-layouts)
7. [Auth, session, and tenancy](#7-auth-session-and-tenancy)
8. [Permissions and roles](#8-permissions-and-roles)
9. [State management (Vuex)](#9-state-management-vuex)
10. [API layer](#10-api-layer)
11. [Real-time (Echo / socket.io)](#11-real-time-echo--socketio)
12. [Components and the in-house design system](#12-components-and-the-in-house-design-system)
13. [Plugins, mixins, utils, constants](#13-plugins-mixins-utils-constants)
14. [Styling, icons, forms](#14-styling-icons-forms)
15. [Third-party integrations](#15-third-party-integrations)
16. [Build, config, environments, deploy](#16-build-config-environments-deploy)
17. [Code graph (graphify)](#17-code-graph-graphify)
18. [Tests and quality](#18-tests-and-quality)
19. [Team workflow and conventions](#19-team-workflow-and-conventions)
20. [Existing documentation: how far to trust it](#20-existing-documentation-how-far-to-trust-it)
21. [Migration hotspot inventory](#21-migration-hotspot-inventory)
22. [Known quirks, dead code, and risks](#22-known-quirks-dead-code-and-risks)
- [Appendix A — how to re-measure](#appendix-a--how-to-re-measure)

---

## 1. At a glance

| | |
| --- | --- |
| What | Appliance.io Point of Sales: the in-store and back-office app for appliance dealers (quotes, orders, inventory, delivery routing, payments, accounting reports, settings, e-commerce website settings) |
| Framework | Nuxt **2.18.1**, Vue **2.7.16**, JavaScript (no TypeScript), Webpack 4 |
| Rendering | Universal **SSR** (`nuxt build` + `nuxt start`); about 10 plugins are client-only |
| Backend | A separate **Laravel REST API** (`BASE_URL`), plus a Laravel Echo socket.io server (`SOCKETIO_HOST`) |
| Size | 269 pages · 604 components (164k lines) · 126 Vuex store files (25.6k lines) · 29 mixins · 45 utils · 29 constants · 15 plugins |
| Tests | 11 Jest spec files; no CI step runs them |
| Activity | 20.8k commits in total; about 505 in the last 6 months, about 3 active contributors |

## 2. Stack and versions

Installed versions are read from `node_modules/*/package.json`. `package.json` ranges are often older
than what is installed (for example `nuxt ^2.6.3`, but 2.18.1 is installed).

| Area | Package (installed) | Notes |
| --- | --- | --- |
| Core | nuxt 2.18.1, vue 2.7.16, vue-router 3.6.5, vuex (via Nuxt) | `.nvmrc` = 20; engines `node >=18` |
| Nuxt modules | @nuxtjs/axios 5, @nuxtjs/auth 4.9.1, bootstrap-vue/nuxt, @nuxtjs/laravel-echo 1.1.0, @nuxtjs/sentry 5.1.7 (@sentry/browser 6.19.7), nuxt-basic-auth-module 1.4.1, local `modules/integrations.js` | |
| UI kit | bootstrap-vue **2.0.0-rc.27**, bootstrap 4.6.2, element-ui 2.13 (DatePicker and TimePicker only) | |
| Forms | vee-validate **2.2.15** | |
| Inputs and widgets | vue-multiselect 2, v-calendar 2.4, vuejs-datepicker, vue2-editor (Quill), @editorjs/*, vuedraggable 2, vue-virtual-scroller 1, vue-carousel, vue-js-toggle-button, vue-slider-component, portal-vue 2, vue-lazyload | `vue-numeric` is a dependency but unused |
| Charts and calendar | chart.js 2.8 + vue-chartjs 3, @fullcalendar/vue 6 | |
| Maps | vue2-google-maps 0.10 + `static/js/oms.js` (OverlappingMarkerSpiderfier) | |
| Real-time | laravel-echo 1.19.0, socket.io-client 2.5.0 | pusher-js is not installed |
| Payments | @adyen/adyen-web 6.19, @adyen/adyen-platform-experience-web 1.9 | |
| Analytics | @amplitude/unified 1.0.0-beta.38, Google Analytics (gtag), Sentry | |
| Utilities | lodash, moment-timezone, libphonenumber-js, i18n-iso-countries, jsbarcode, print-js, lottie-web, heic2any, compressorjs, @svgdotjs/svg.js, detect-browser | |
| Styling | sass 1.89, sass-loader 10, @phosphor-icons/web | |
| Tooling | eslint 8 (vue, nuxt, prettier plugins), prettier 3, husky 8, lint-staged, commitlint (conventional), jest 29 + vue-jest 3 + @vue/test-utils 1 | npm, lockfile v3 |

## 3. Repository layout

| Path | Contents |
| --- | --- |
| `pages/` | 269 `.vue` route files (Nuxt file routing; nesting uses `index.vue` + `index/`) |
| `components/` | 604 `.vue` + `utilities/Responsive.js`; 27 top-level folders (see [§12](#12-components-and-the-in-house-design-system)) |
| `store/` | Vuex modules mode: `index.js` + 125 modules (subfolders `dashboard/`, `reports/`, `settings/`) |
| `layouts/` | `admin.vue`, `default.vue`, `blank.vue`, `onboarding-website.vue` (no `error.vue`) |
| `middleware/` | `maintenance.js` (active), `permission.js` (dead) |
| `plugins/` | 15 plugins (see [§13](#13-plugins-mixins-utils-constants)) |
| `mixins/` | 29 mixins (`homeVisit/`, `quote/` subfolders) |
| `utils/`, `constant/`, `helper/`, `directives/`, `types/` | Helpers, option lists, a map style, one directive file, constant enums (no TypeScript) |
| `modules/integrations.js`, `integrations/ga.client.js` | Local Nuxt module that auto-registers every file in `integrations/` as a plugin |
| `app/router.scrollBehavior.js` | Always scrolls to `{x:0, y:0}` |
| `assets/style/` | SCSS theme (about 15k lines), fonts, Adyen CSS overrides; Lottie JSON |
| `static/` | 261 files (3 MB): icons, logos, favicon, `js/` (intercom, oms, qrcode.min, userback), `notification.mp3` |
| `__tests__/` | 11 Jest specs |
| `docs/` | 437 Markdown files, mostly AI-generated (see [§20](#20-existing-documentation-how-far-to-trust-it)) |
| Root | `nuxt.config.js`, `Dockerfile`, `Jenkinsfile`, `bitbucket-pipelines.yml`, `deploy_to_{dev,staging}_server.sh`, `sonar-project.properties`, `CLAUDE.md`, `.github/copilot-instructions.md`, `prompt.txt`, `component-prompt.txt` |

## 4. Business domains

This is a working map from domains to code. The grouping comes from page sections, store modules,
and endpoints.

| Domain | Pages | Main store modules | Main components |
| --- | --- | --- | --- |
| Quotes and orders (checkout) | `my-quotes/`, `my-orders/`, `product/_id` | order (2,212 lines), quote, orderSchedule, return, reschedule, fulfillmentTypes, haulAway(Control), damageWaiver, install(Rules), homeVisit, packageDeals, coupon, rebate, warranty, specialOrder | `components/invoice/` (OrderTable 3,388 lines, QuoteTable, OrderSchedule, payments, OrderReturn, FulfillmentType), `features/quote` |
| Customers (CRM) | `customers/` | customer, customerJob, customerNotes, customerNotification, leadSourceOptions | `form/CustomerNew`, `form/CustomerCreate` |
| Inventory, catalog, pricing | `inventory/`, `transfer-inventory/`, `purchase-orders/`, `skudeck/`, `settings/basic-settings/product-*` | inventory (1,718), bulkInventory, transferInventory, reconcileInventory, costCheck, adc/dmiInventory, product, brand, category, pricing, pricingZone, rule, priceTag, priceTagV3, skudeck, vendor* | `inventory/`, `TransferInventory/`, `skudeck/`, `pages/receive-inventory` |
| Delivery and routing | `deliveries/`, `routing/` | delivery (1,127), deliveryRouting, deliveryMethod/Zone/Times/Options, driver, truck, timeLimit, partner | `deliveryRouting/` (maps, stops, trucks), `delivery/ScanOut`, `dashboard/DeliverySchedule` |
| Accounting and reports | `accounting/` (28), `reports/` (49), `management-tools/` (16) | accounting (1,064), accountReceivable, balanceSheet, incomeStatement, salesTax, salesKpiReport, spiffReport, leaderboard, `reports/*` | `reports/`, `table/`, `admin/table` |
| Payments | inside quote/order flows, `reports/aio-pay-payout-report` | payment, AIOPay, aioPaySettings, adyenTerminal | `components/payment/` (AIOPay*, financing, refunds) |
| Company, users, permissions | `settings/basic-settings/{company,users}`, `my-profile/` | company, location, store, employee, role, permission, navigation, userSetting | `settings/Users`, `settings/Location` |
| Website and e-commerce | `settings/website-settings/` (blog, SEO, e-commerce, wholesale), `website-onboarding/` | `settings/*`, onboardingWebsite, wholesale* | `OnboardingWebsite/`, `settings/Blog`, `settings/E-Commerce` |
| Onboarding and sign-up | `onboarding/`, `sign-up/_id`, `login/`, `reset-password/` | onboarding, sign-up, reset-password | `Onboarding/` |
| Dashboard and notifications | `index.vue` | dashboard, systemAlerts, internalNotifications, chat | `dashboard/`, `MyNotification/` |

Payment providers that come up in code and docs: Adyen / AIO Pay, BlockChyp, Stripe (socket event
names), and financing (Acima, Snap, Synchrony, Wells Fargo, per `docs/overview.md`). Protection-plan
providers include CPS, EPIC, internal, and Mulberry.

## 5. Routing and pages

**Shape**
- 269 page files: 119 top-level route records and 150 nested child routes.
- 66 `index/` folders. 64 pages render `<nuxt-child>`, and two components (`orders/OrderPage.vue`,
  `OnboardingWebsite/Steps.vue`) host the child outlet.
- Nesting goes up to 3 levels deep, for example
  `settings/website-settings/website-e-commerce/index/my-website/index/content/index/_steps`.
- 24 dynamic segments: `_id` 17, `_status` 5, `_steps` 3, `_provider` 1. Some are flat `_x.vue` files.
- `subFolders: true` in `nuxt.config.js:74` has **no routing effect** (it is a `generate` option).

**Sections** (page count · purpose)

| Section | Pages | Purpose / notable routes |
| --- | --- | --- |
| `index.vue` | 1 | Dashboard; picks the widget set by `role_id` (`pages/index.vue:107-115`) |
| accounting | 28 | Financial statements with `delivered-sales` / `written-sales` tabs. Index redirects to `/reports`. |
| customers | 6 | `index/{individual,company}`, `create`, `edit/_id`, `profile/_id` (2,411 lines) |
| deliveries | 7 | Delivery list, logs, preview, `scan-out` |
| inventory | 13 | Store / DMI / ADC inventory, reconcile worksheets, transfers, cost check, `stock-movement/_id` |
| management-tools | 16 | Damage allowance, reschedules, returns, spiffs, floor model, sales KPI, sell-throughs. Index redirects to `/reports`. |
| my-orders | 4 | `index/all`, `index/_status`, `edit/_id` (2,354 lines) |
| my-quotes | 5 | `index/{active,expired}`, `create`, `edit/_id` |
| purchase-orders | 9 | Open / requested / history, goods receipt, receive by PO / FIFO |
| reports | 49 | Reports hub (navigation tree from the backend) with about 25 reports, including AIO Pay payouts (new and old) |
| settings | 104 | `basic-settings` (company, delivery, installs, packages, payment methods, catalog, pricing, promos, protection plans, terms, users), `advanced-settings` (accounting, delivery automation, digital price tags v3, notifications), `website-settings` (blog, SEO, e-commerce, wholesale) |
| transfer-inventory | 6 | In-transit / log / add / edit / receive (duplicates part of `inventory/transfer-inventory`) |
| routing | 2 | Delivery route planner, `log/_id` |
| onboarding · website-onboarding | 2 · 2 | Guest company sign-up wizard · authenticated website setup wizard |
| login · reset-password · sign-up | 2 · 2 · 1 | `/login`, `/login/access` (PIN), reset, invite sign-up |
| Others | — | `change-location`, `directory`, `integrations`, `my-profile/_id`, `refer-and-earn`, `skudeck`, `maintenance.vue`, `new-pages` (placeholder) |

**Page-level Nuxt 2 APIs**

| API | Pages | Notes |
| --- | --- | --- |
| `asyncData` | 97 | 60 destructure `redirect`. 35 tab parents redirect to their default child with `if (route.name === '<parent>') redirect(...)`. |
| `fetch()` | 3 | All use the **legacy** context signature `fetch({ store, route })` (e.g. `inventory/stock-movement/_id/index.vue:63`). |
| `head` | 133 | 50 `head()` functions, 83 `head:` objects. `titleTemplate: '%s - Appliance.io'`. |
| `transition: 'slide'` | 229 | Uses Vue 2 class names `.slide-enter` (`assets/style/components/_animation.scss:2-18`) |
| `layout:` | 213 | 109 of these sit on child pages, where they have no effect (Nuxt 2 takes the layout from the outermost page) |
| `auth:` | 5 | `false`: maintenance, reset-password/reset/_id, sign-up/_id. `'guest'`: onboarding, reset-password. |
| `validate()` · `watchQuery` · `middleware:` | 1 · 1 · 0 | |
| `beforeRouteLeave` / `beforeRouteEnter` | 52 / 5 | |

**Route names are a contract with the backend**
- The sidebar builds links as `{ name: navigation.slug }`, with slugs supplied by the API
  (`components/layout/Sidebar.vue:22,48,119`), for example `customers-index-individual`.
- 155 route-name literals containing `-index` appear in 81 files.
- `$route.name` is read 262 times in 109 files, and there are 244 `$router.push` / `replace` calls.
- Any change in how routes are named breaks navigation unless the backend slugs change too.

**Scroll behaviour:** `app/router.scrollBehavior.js` always scrolls to the top. It ignores
`savedPosition` and hashes, and uses the vue-router 3 `{x, y}` keys.

## 6. Layouts

How layouts are applied in practice (to the 119 top-level route pages):

| Layout | Pages | What it mounts |
| --- | --- | --- |
| `admin` (402 lines) | 102 | The authenticated shell. See the details below. |
| `default` | 15 | ScreenTimeout, SystemAlertBanner, `<nuxt/>`, and the main **socket setup** (logout, system-alerts, sms-status channels, plus `watchPermissionUpdate`) |
| `blank` | 1 (login) | `<div><nuxt/></div>` |
| `onboarding-website` | 1 | A trimmed copy of admin (still named `'LayoutAdmin'`) |

`admin` in detail:
- Renders only when `$auth.loggedIn`.
- Mounts the Sidebar, plus either Header or HeaderMobile (`<app-responsive>`, 992px breakpoint). It
  also mounts the SystemAlertBanner, the notifications modal, the offline and account status
  components, and `<portal-target name="modal">`.
- On every route change it restarts Intercom and sends a GA page view.
- In `created` it sets the moment default timezone. In `mounted` it starts `authListener` and the
  Echo permission watcher.
- It reloads the page at midnight.

## 7. Auth, session, and tenancy

**Module**
- `@nuxtjs/auth` v4 with the `local` strategy (`nuxt.config.js:168-196`).
- Endpoints: `login` (POST, reads `token`), `logout` (POST), `user/store` (GET; the whole response
  is the user object).
- Bearer token, cookie prefix `auth.`, `resetOnError: true`.
- Redirects: `login` and `logout` go to `/login`, and `home: false` (so `auth: 'guest'` never
  redirects logged-in users).
- Global router middleware: `['auth', 'maintenance']`.

**Token storage**
- The token is stored as `auth._token.local` in both the cookie and localStorage.
- It is read directly in `plugins/laravel-echo.js:7`, `pages/login/access/index.vue`, and
  `utils/authListener.js:5` (a cross-tab `storage` listener that reloads the page).
- `nuxtServerInit` (`store/index.js:125-146`) reads the cookie, stores the host header, and, when
  the user is logged in, loads stores, user settings, notifications, the price-tag active store, the
  company switch, and the first-year quote.

**Login flows** (`pages/login/index.vue`, layout `blank`)
1. `checkLogin`: POST `v-login` returns the company and store, then sets the `x-company-x` header
   and fetches `invited-stores`. A 403 opens a "force" modal that retries with
   `delete_session=true` (one session per user).
2. `submit`: `$auth.loginWith('local', {email, password, store_id, is_admin: 0, type: 'default'})`,
   then a Lottie splash, then a hard redirect to `/` (or to `/settings` for the Website Admin role).
3. Google sign-in: GIS is loaded on demand. The credential is sent through the same `loginWith` call
   with `type: 'social-auth'`.
4. `?token=` handoff: GET `check-in` with that Bearer token, then `$auth.setUserToken`. Switching
   between the POS, test, live, and data apps works this way: `pos-app/switch` or `catalog-app/switch`
   returns a token, then the app sets `window.location = <otherApp>/login?token=…`
   (`mixins/header.js:228-254`).
5. `/login/access`: a PIN-based store-access login (`is_admin: 3`). It keeps a `backup_token` in
   localStorage.

**Logout and session changes**
- Logout: `$auth.logout()`, then `$amplitude.reset()`, then a hard redirect to `/login`.
- Forced logout arrives over sockets ([§11](#11-real-time-echo--socketio)).
- Switching company: POST `switch-company` with `{email, db_name}` returns a new token, then
  `setUserToken` and a hard reload. This suggests one database per tenant.
- Changing location: POST `user/change-location`, then re-fetch `user/store`, then reload.

**The `$auth.user` shape** (259 references in 111 files)

| Group | Fields |
| --- | --- |
| Identity | `user_id`, `user_code`, `email`, `fullname`, `display_picture`, `last_login` |
| Permissions | `role.role`, `role_id`, `navigations[]`, `features[]`, `god_mode`, `hide_brand_pricing`, `has_online_order_return_permission`, `is_sales_person`, `dashboard_menu` |
| Tenant (`companies`) | `code` (prefix for every socket channel), `name`, `timezone`, `has_route_access`, `company_type` (2 = delivery provider), `partner_id`, `primary_color`, `website_address` |
| Location | `store` (`store_id`, `store_name`, `lat`, `lng`), `default_store` |

**Timezone:** `plugins/timezone.js` injects `$setMomentDefaultTz`, which calls
`moment.tz.setDefault(companies.timezone)` and falls back to `America/Chicago`. It is called from the
layouts' `created` hook, which also runs during SSR, so it changes the moment singleton for the whole
server process.

**Onboarding:** `?registerToken` is compared on the client against `$config.registerToken`. The
onboarding session uses cookie `session_id`, sent as header `X-Onboarding-Token`.

## 8. Permissions and roles

All of this comes from the `$auth.user` object (GET `user/store`). There is **no route-level
enforcement**: `middleware/permission.js` is never registered, and the `checkPermission` action it
dispatches does not exist.

| Mechanism | Where |
| --- | --- |
| Navigation tree from the backend | Builds the sidebar. Reports and settings hubs fetch subtrees by navigation id. |
| `asyncData` guards | 4 pages check `navigations` (integrations and refer-and-earn redirect to `/`). Routing checks `has_route_access`. 2 pages guard on role. |
| `mixins/permissions.js` (124 lines, about 53 importers) | 7 role computeds (Super Admin, Store Manager, Buyer, Delivery Manager, Third Party Delivery Manager, Website Admin, Sales Associate), 2 navigation checks, and about 20 `features.some(f => f.name === '…')` checks |
| Inline checks | `role.role === '…'` literals, `role_id === '1'`, and `role_id` values `'9'`, `'10'`, `'11'` for dashboard variants |
| Live revocation | Echo event `PermissionUpdate` on `{code}-permission-update-{uid}` forces a logout (`plugins/global.js:299-313`) |

Feature names compared in code (32): Order Auditor, Delivery Settings Manager Override, Add-on
Price-Override, Special Order Item Action, Inventory Management, User Permission, Terminal Setting
Permission, Tax Rate Override, Tax Exempt Customer, Storage Location Management, Show All Sales Person
{Spiffs, Protection Plan, Commission} Report, Routing Notes, Returns on Orders, Replacement Model
Permission, Quote/Order Reassign, Payment Setting Permission, Override Restocking Fee, Override
Inventory Reservations, Order Item Management, Location Setting Permission, House Deal Button, Edit
Cost Commission Report, Delivery Date Booked, Delivery Auditor, Customer Export, Credit Lines Access,
Company Setting Permission, Bypass Delivery Capacity Limit, Bypass Checkout Lock Permission, Account
Credit Returns.

## 9. State management (Vuex)

**Setup**
- Nuxt modules mode with `store/index.js` and `strict = false`.
- Namespaces come from file and folder names (for example `settings/meta`); no module sets
  `namespaced` itself.
- Every module exports `state`, `mutations`, and `actions` as named exports. 18 modules also have
  getters.

**Actions are thin HTTP wrappers.** The typical action is an `$axios` call, an optional `commit`, then
resolving with `response.data`. See `store/brand.js:37-72` for both styles.
- There are about 553 `new Promise` wrappers (which reject with `error.response`) and about 552
  `async` methods (which throw the raw axios error).
- So error shapes differ between callers.
- Some actions catch an error without rejecting, so their promise never settles (for example
  `store/infomarks.js:10-12`).

**Largest modules:** order 2,212 lines, inventory 1,718, delivery 1,127, accounting 1,064, customer
733, quote 672, deliveryRouting 653, priceTag 619.

**How components use the store**

| Usage | Count |
| --- | --- |
| `...mapState` / `...mapActions` / `...mapMutations` / `...mapGetters` | 863 / 565 / 252 / 45 |
| `this.$store.dispatch` / `.commit` / `.state` | 26 / 45 / 12 |
| `store.dispatch` in page `asyncData` | 128 in 54 files |

**Cross-module coupling is low:** 13 live `rootState.X` reads, 1 `rootGetters`, and 5
`{ root: true }` (all in `haulAwayControl.js`).

**Side effects in the store**
- Toasts through `this.$root.$bvToast` (catalogChangelog, systemAlerts).
- `this.$toast` in `reports/homeVisitSurveyReport.js`, which is never injected, so these calls would
  throw.
- `$auth` is used in 3 modules.

## 10. API layer

**Config**
- `@nuxtjs/axios` with `baseURL: process.env.BASE_URL` (set at build time) and `progress: true`.
- `@nuxtjs/auth` adds the `Authorization: Bearer` header.

**`plugins/axios.js` (31 lines)**
- It only sets JSON headers and toggles the root `loadingTable` flag.
- The URL-exclusion check in `onResponse` reads `config.url` from a response object, so it is always
  empty and every response clears the flag.
- There is **no global error, 401, toast, or redirect handling.**
- `resetOnError` only covers calls made through `$auth`.

**Where calls live**
- 1,132 HTTP calls are in the store (`.get` 517, `.post` 294, `.put` 168, `.delete` 79, plus the
  unwrapped `$get` / `$post` variants).
- Only 11 call sites are in the UI, mostly file and blob downloads.
- `$axios.CancelToken` is used 75 times and `isCancel` 48 times.

**Endpoint style**
- Relative, kebab-case, resource-first paths that don't follow REST verbs, for example
  `rule/update/:id` or `user/message-center/multiple-update`.
- Laravel `_method` spoofing appears 73 times, and a few `v2/` paths exist.
- Top prefixes: inventory, order, report, price-tag, customer, user, delivery-route, delivery.
- A few hard-coded absolute URLs exist (`store/product.js:240`, `store/orderSchedule.js:238,250`).

**Custom headers:** `x-company-x` (before login), `X-Onboarding-Token`, and an explicit Bearer token
for `check-in`.

**Responses**
- Laravel JSON: `response.data`, often `response.data.data`.
- Pagination comes in two shapes: paginator fields at the top level, or a nested `meta` object.

**Errors**
- Handled in each component with `this.$root.$bvToast.toast(...)` (744 occurrences in 333 files),
  reading `error.response.data.message`.
- Explicit status checks are rare: 401 ×2, 403 ×4, 422 ×15.

**Exports:** `plugins/export-data.js` injects `$exportingData` (47 users) and `$toPdf`. The flow is a
GET that returns a file URL, then a second fetch of that URL with `baseURL: ''` as a blob or
arraybuffer.

## 11. Real-time (Echo / socket.io)

There are two Echo instances:
- The **custom** `plugins/laravel-echo.js` (client-only) creates `window.Echo` with
  `broadcaster: 'socket.io'`, `host: $config.socketIoHost`, websocket transport, and 5 reconnection
  attempts. Its Bearer token is read **once at boot** from localStorage, and the hard reloads after
  login, switching, and logout re-create it. This is the instance the code uses: 35 references in 13
  files.
- The `@nuxtjs/laravel-echo` module is configured with no broadcaster, so its `$echo` has a null
  connector and is **never used**.

`{code}` = `$auth.user.companies.code`, `{uid}` = `$auth.user.user_id`:

| Channel | Type | Event | Where |
| --- | --- | --- | --- |
| `{code}-logout` | private | `Logout` | `layouts/default.vue:188` |
| `{code}-logout-{uid}` | private | `LogoutUser` | `mixins/header.js:87` |
| `{code}-permission-update-{uid}` | private | `PermissionUpdate` | `plugins/global.js:302` |
| `{code}-system-alerts` | public | `SystemAlertCreated/Updated/Deleted` | `layouts/default.vue:143-156` |
| `{code}-sms-status`, `sms-alert-system-check` | public | `SmsSystemStatusChanged` | `layouts/default.vue:158`, `store/systemAlerts.js:278` (no caller) |
| `{code}-message-center-{uid}` | private | `MessageCenter` | `components/MyNotification/Notification.vue:285` |
| `{code}-payment-{quoteId}` | public | `StripePayment` | `mixins/quote/quoteWebSocket.js:35-50` |
| `{code}-payment-rebate-{rebateId}` | public | `RebatePayment` | `mixins/quote/quoteWebSocket.js:60-80` |
| `{code}-payment-lock-{orderId}` | public | `PaymentLockChanged` | `components/invoice/InvoicePayment.vue:778-801` |
| `{code}-failed-{id}` | public | `AioPayFailedEvent` | `components/payment/AIOPayPhonePayment.vue:247-261` |
| `{code}-customer-notification-link-order-{orderNo}` | private | `CustomerScheduleLinkNotification` | `pages/my-orders/edit/_id/index.vue:2109` |
| `{code}-routing-{date}-{method}` | private | `RoutingStatusUpdate` | `pages/routing/index.vue:395-437` |
| `delivery-route-session-{method}-{date}` | private | `DeliveryRouteSession` (locks the route for concurrent editors) | `pages/routing/index.vue:441-468` |
| `{code}-price-sync-status` | private | `PriceSyncStatus` | `settings/basic-settings/product-pricing/index.vue:274` |
| `private-{code}-price-tag-bind` | public (prefixed by hand) | `PricetagBind` | `digital-price-tags-v3/.../product-and-tags/index.vue:613` |

## 12. Components and the in-house design system

**Registration**
- There is **no auto-import**: `nuxt.config.js` has no `components:` key. Every component is imported
  explicitly into a local `components: {}` block.
- 3,311 imports use the `@/` or `~/` alias, and 142 are relative.
- There are no lazy component imports.
- The global components are the 10 `Vue.component` calls in `plugins/client.js` plus every
  bootstrap-vue `b-*` component.

**Naming:** the `App*` prefix is an **alias given at import time, not a filename**, for example
`import AppButton from '@/components/utilities/Button'`. In templates this shows up as `<app-button>`
(1,298 uses), `<app-input>` (398), `<app-select>` (359), `<app-modal>` (346), and so on.

**The design system is `components/utilities/` (101 files).** It is imported in 718 files and accounts
for about 78% of alias imports. The most-imported components:

| Component | Imports | Component | Imports |
| --- | --- | --- | --- |
| Button | 465 | Breadcrumb | 88 |
| Modal (portals to `modal`) | 250 | PriceInput | 78 |
| Spinner | 240 | Datepicker (v-calendar) | 72 |
| Input | 230 | MultipleCheckboxInput | 67 |
| Alert | 160 | PageLoader | 52 |
| Badge | 149 | ExportButtons | 47 |
| TotalRecord | 111 | DatepickerRange | 43 |
| BackLink | 89 | modal/ConfirmModal | 40 |

Some `app-*` tags wrap third-party components rather than in-house ones:

| Tag | What it is |
| --- | --- |
| `app-select` | vue-multiselect, imported in 190 files |
| `app-table`, `app-pagination` | **Deep imports** from `@/node_modules/bootstrap-vue/es/components/...` (34 imports) |
| `app-calendar`, `date-picker` | v-calendar, registered globally |
| `app-monthpicker` | vuejs-datepicker |

**Folders** (27 top level):
- utilities 101, invoice 81, settings 73, admin 49, form 32, inventory 26, dashboard 26,
  deliveryRouting 23, modal 22, payment 19, pages 18, reports 17, OnboardingWebsite 16,
  integrations 14, features 13, skudeck 11, delivery 11, table 10, Onboarding 9, orders 8,
  layout 7, TransferInventory 7.
- The rest are smaller.

**Largest components:** invoice/OrderTable 3,388 lines, QuoteTable 2,769, OrderSchedule 2,349,
CheckStockModal 1,789, OrderReturn 1,660, Notes 1,611, inventory/UnitDetailManager 1,603,
InvoiceTotalSummary 1,553.

**UI library usage**

| Library | Usage |
| --- | --- |
| bootstrap-vue | `<b-*>` in 329 files (1,049 tags: b-table 178, b-tab 127, b-pagination 107, radios, dropdowns, collapse, checkbox). `v-b-tooltip` 600. `$root.$bvToast` 737. `$bvModal` 0, and only 1 `<b-modal>`. `plugins/global.js:10` mutates the BTable default sort direction. |
| Bootstrap 4 CSS utilities | Everywhere (`d-flex` 2,602 occurrences in 633 files) |
| element-ui | `<el-time-picker>` in 7 files, but the full theme CSS is imported globally |
| vue-multiselect | 190 files, CSS loaded from a CDN `@import` |
| vue-js-toggle-button | 63 files |
| vue2-editor (Quill) | 12 components (client-side `require`) |
| vue2-google-maps | 6 files (`<gmap-*>` 13 tags) |
| vuedraggable | 8 |
| vue-carousel | 4 |
| print-js | 6 (via `utils/printJs.js`) |
| Single-use | vue-chartjs (1 global, 3 users), FullCalendar (1), editor.js (1), virtual-scroller (1), slider (1), Lottie (2), Strich (1) |

**Client-only handling:** `<client-only>` appears 176 times in 126 files, and `process.client`
requires appear 29 times.

## 13. Plugins, mixins, utils, constants

**Plugins** (in the order of `nuxt.config.js:91-137`)

| Plugin | Runs on | What it does |
| --- | --- | --- |
| `global.js` | both | element-ui pickers; BTable default; vee-validate with `fieldsBagName: 'vvFields'` and **8 custom rules**; `Vue.prototype._` (lodash) and `.moment`; `Vue.filter('truncate')`; a **global `Vue.mixin`** (`isDeliveryProvider`, SVG/QR/barcode helpers, Intercom, `watchPermissionUpdate`, `checkNetworkStatus`, …); a `warnHandler` that hides `.native` warnings |
| `directive.js` | both | `v-money` (505 uses), `v-width` / `v-height`, `v-table-sticky-header` (34), `v-table-sticky-column`, `v-append-select`, `v-click-outside`, `v-closable`, all using **Vue 2 hook names** (`bind`, `componentUpdated`, `unbind`) |
| `axios.js` | both | See [§10](#10-api-layer) |
| `timezone.js` | both | `$setMomentDefaultTz` |
| `google-maps.js` | both | vue2-google-maps (geometry, places) |
| `client.js` | client | Global components (carousel, calendars, monthpicker, toggle, line charts, virtual scroller), VueLazyload, PortalVue |
| `laravel-echo.js` | client | `window.Echo` |
| `lottie`, `open-new-tab`, `export-data`, `adyen`, `editor`, `amplitude` | client | `inject`: `$lottie`, `$openNewTab`, `$exportingData` / `$toPdf`, `$adyen`, `$editor`, `$amplitude` |
| `quill-resize-module.js` | client | Quill resize module and image format |
| `close-sibling-dropdowns.js` | client | A `MutationObserver` that closes sibling dropdowns through `el.__vue__` |

**Mixins:** 29 files (2,477 lines), used by 105 components and pages, plus the global mixin above.

| Mixin | Users |
| --- | --- |
| `permissions` | 53 |
| `homeVisit/warehouse` | 13 |
| `deliveryRouting` (`$nuxt` event bus) | 12 |
| `deliveryDate` | 5 |
| `homeVisit` | 5 |
| `onboarding` | 5 |
| `screen-size` | 4 |
| `header` (search, logout listener, company/app switch) | 3 |
| `quote/*` (payment orchestrator, PDF service, WebSocket) | — |
| scan-out mixins | — |
| `cutOffTime`, `download-file`, `download-image` | 0 (unused) |

**Utils:** 45 files.

| Area | Files |
| --- | --- |
| Money | `toMoney` (default export, 16 files) plus the `v-money` directive |
| Tax | `calculateTax` |
| Dates | `date`, `years`; the real date layer is **moment-timezone** (`this.moment(` 511 calls in 153 files; any `moment(` 781 calls in 215 files) |
| Serial numbers | `serialNumber` (brand-specific cleansing) |
| Files | `download`, `compressImage`, `convertHeic`, `printJs`, `barcode`, `priceTagSvg` |
| Other | string-case helpers, `copyText` (24), `jsLoader` (`OnDemand` script loader), `authListener`, `googleAnalytics` |

**Constants and the rest**
- `constant/` (29) holds option lists and maps, for example `orderFIlters` (250 lines), `dayFilter`,
  `mapStyles`, `timezone` (`DEFAULT_TZ`), and `customerClass`.
- `helper/index.js` repeats the map style.
- `directives/number-only-directive.js` is used only by `PhoneInput`.
- `types/` holds mutation-name constants for 2 modules.

**Implicit globals**
- `_` is used without an import in `plugins/directive.js` and `plugins/global.js`.
- `QRCode` comes from a head script.
- `Echo`, `google`, `$nuxt`, `gtag`, `dataLayer`, `OverlappingMarkerSpiderfier`, and `Calendly` are
  declared as ESLint globals.

## 14. Styling, icons, forms

**Global CSS**
- `assets/style/app.scss` (390 lines) loads CDN imports (multiselect CSS, the Figtree and JetBrains
  Mono fonts), then the variables and mixins, the **full element-ui theme**, the themed
  **`bootstrap/scss/bootstrap.scss`**, 50 component partials, IcoFont, and 2 page partials.
- The bootstrap-vue module also injects the stock `bootstrap.css` and `bootstrap-vue.css`, so
  **Bootstrap CSS loads twice**.

**Theme** (`_variable.scss`, 509 lines)
- Colour scales: gray, brand, yellow, green, blue, red, orange, copper.
- `$primary: $brand-80`.
- A `$theme-colors` map with every scale step, which generates `text-*`, `bg-*`, and `btn-*` classes.
- `$font-size-base: .875rem`.
- Mixins for media queries, `hex-to-rgba`, pulse effects, and the brand gradient.

**Component styles**
- 283 `<style>` blocks: 211 scoped, 248 SCSS, 72 unscoped.
- `::v-deep` 46; no `>>>` or `/deep/`.
- Each SFC imports `~/assets/style/variable` by hand (121 times); there are no global style
  resources.
- Sass deprecation warnings are silenced in `nuxt.config.js`.

**Icons:** **Phosphor** via CSS classes (`ph ph-<name>`, 1,511 occurrences in 452 files). The
migration from Material Icons finished in Sept–Oct 2026. IcoFont is loaded but used only for
price-tag SVG fonts.

**Forms:** **vee-validate 2** (directive API).

| Pattern | Files / occurrences |
| --- | --- |
| `v-validate` | 149 / 498 |
| `errors.first(` | 147 / 520 |
| `errors.has(` | 85 / 335 |
| `$validator` | 146 / 395 |
| `validateAll()` | 113 |
| `data-vv-as` | 118 |
| `inject: ['$validator']` | 1 |
| `ValidationProvider` / `ValidationObserver` | 0 |

- Most validation sits on the custom `app-*` inputs, which use the Vue 2 `value` prop and
  `$emit('input')`.
- There are 13 custom rules (8 global ones in `plugins/global.js` and 5 local ones).
- Typical example: `components/settings/Users/ChangePasswordForm.vue:8-65`.

## 15. Third-party integrations

| Integration | How it's wired | What uses it |
| --- | --- | --- |
| Adyen Platform Experience | `plugins/adyen.js`: lazy `import()` plus CSS overrides | 8 payout, transactions, and disputes report pages (new and old) |
| Adyen Web (card drop-in) | `components/payment/AIOPayPhonePayment.vue:123-366`; company code `pcF` (Devixel) forces test mode | `invoice/InvoicePayment.vue` |
| AIO Pay | `store/AIOPay.js` (`adyen/*` onboarding), `aioPaySettings`, `adyenTerminal` | Payment methods settings, terminal payments |
| BlockChyp, Stripe | Mentioned in 9 files. Payment results arrive over sockets (`StripePayment`). | Quote payment |
| Amplitude | `plugins/amplitude.js`: full autocapture, **100% session replay**, opts out internal domains, no-op without a key | `store/milestone.js`, logout reset |
| Sentry | `@nuxtjs/sentry` config only (DSN and environment); no manual calls | — |
| Google Maps | vue2-google-maps + `oms.js` | Routing maps, delivery map, address autocomplete, location forms |
| Google Analytics | `integrations/ga.client.js` (`$ga.load`) | Page views from the admin and onboarding-website layouts |
| Google sign-in | GIS loaded on demand | Login, sign-up |
| Intercom | `static/js/intercom.js` + global mixin; rebooted on every route change | Support messenger |
| Userback | `static/js/userback.js` head script | Feedback widget (replaced Featurebase on 2026-08-05) |
| Strich | Head script from `STRICH_JS_URL`; uses **mangled globals** `tA` / `lA` | Digital price tags v3 (MAC address scanning) |
| Calendly | Loaded on demand | Website onboarding |
| QRCode / jsbarcode / print-js / Lottie / editor.js / Quill | See [§12](#12-components-and-the-in-house-design-system) and [§13](#13-plugins-mixins-utils-constants) | |

The `static/js/userback.js` and `static/js/intercom.js` files contain hard-coded third-party IDs and
tokens, and so does `plugins/global.js`. Don't copy those values into this workspace.

## 16. Build, config, environments, deploy

**`nuxt.config.js`**
- No `ssr`, `mode`, or `target` key, so it runs universal SSR.
- `head`: `titleTemplate`, robots `noindex`, favicons, and 5 global head scripts (Strich, Userback,
  QRCode, oms, Intercom).
- `loading` bar colour `#141414`.
- `css`: the global stylesheet plus two Phosphor CSS files.
- `plugins` and `modules` as listed in [§13](#13-plugins-mixins-utils-constants) and [§2](#2-stack-and-versions).
- `router.middleware`: `['auth', 'maintenance']`.
- Configuration for axios, auth, echo, sentry, and basic-auth.
- **`build.extend`** (Webpack only) adds an extra babel `preset-env` to every babel-loader rule and
  silences Sass deprecations.
- `build.transpile`: Adyen platform experience, svg.js, editor.js, Amplitude, FullCalendar,
  web-vitals.
- `extractCSS: { ignoreOrder: true }`.

**Runtime config:** `publicRuntimeConfig` has 15 keys, used through `$config` 34 times. There is no
private runtime config.
- `socketIoHost`, `googleClientId`, `googleAnalyticsId`, `googleMapApiToken`
- `maintenance` (compared as a string)
- `appUrl`, `testServerUrl`, `liveServerUrl`, `dataAppUrl`
- `aioPayClientKey`, `aioPayDevixelClientKey`, `aioPayLiveEnvironment`
- `registerToken`, `amplitudeApiKey`, `websiteBuilderDomain`

**Build-time env only:** `BASE_URL`, `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `BASIC_NAME`, `BASIC_PASS`,
`BASIC_ENABLED`, `STRICH_JS_URL`, `NUXT_PORT`.

**Env file mismatches**
- `MAINTENANCE` and `NUXT_PORT` are used in code but missing from `.env.example`.
- `TEST_SERVER_BASE_URL` and `DATA_APP_BASE_URL` are in `.env.example` but unused.
- `PUSHER_*`, `SERVER_TYPE`, and `CLERK_PUBLISHABLE_KEY` appear only in local env files and are unused.

**Environments**

| Env | Trigger | How |
| --- | --- | --- |
| dev | push to `development` | Bitbucket pipeline SSHes to a VPS and runs `deploy_to_dev_server.sh`: pull, `npm install`, `npm run build`, then pm2 `slymanbros-pos-test` (`npm run start`). The `.env` comes from the infra-code repo. |
| staging | push to `staging` | Same, using `deploy_to_staging_server.sh`: `nvm use` (Node 20), port 3016, `pm2 restart app-staging` |
| prod | Jenkins (`Jenkinsfile`) | Clones the infra-code manifest. The `.env` is **baked into the Docker image** (`node:20-alpine`, `npm ci`, `nuxt build`, `nuxt start` on 3000). Pushes to ECR us-west-1, then `eb deploy` to Elastic Beanstalk. |
| PRs | Bitbucket | **gitleaks secrets scan only**; no lint, test, or build steps |

**Ports:** local dev 3019 (`package.json` `config.nuxt.port`), staging 3016, Docker 3000. Basic auth
(`nuxt-basic-auth-module`) runs as server middleware, so it needs the Node SSR server.

## 17. Code graph (graphify)

| | |
| --- | --- |
| Location | `graphify-out/` at the root of this repo (`graph.json`, `graph.html`, `GRAPH_REPORT.md`, `manifest.json`) |
| Scope | Code only, AST-based: 1,154 `.vue` / `.js` files from `aio-pos` (no docs or images). Built 2026-11-23 at `341775157`. Token cost 0. |
| Size | 6,187 nodes (files, methods, functions), 6,261 edges (`contains` 5,024, `calls` 1,214, imports only 15), 1,146 communities, labelled `<folder>: <dominant file>` |
| How to use | `/graphify query "<question>"`, `/graphify path "A" "B"`, `/graphify explain "X"`, or open `graphify-out/graph.html` |
| Refresh | `bash app-knowledge/rebuild-graph.sh`: code-only AST rebuild, no LLM, aborts without writing if extraction fails. **Don't** use `/graphify --update`. It re-detects docs and images, treats `.vue` as non-code, and launches LLM subagents. |

**Limitation:**
- The AST pass does not follow `import` statements inside `.vue` single-file components. So the graph
  is reliable for "what does this file or function contain and call", but **not** for cross-file
  dependencies.
- Communities are roughly one per file. Only 6 edges cross between communities.
- For dependencies, use the import counts in [§12](#12-components-and-the-in-house-design-system) or
  `rg` (Appendix A).

## 18. Tests and quality

**Jest setup**
- `jest.config.js`: vue-jest + babel-jest, jsdom, the `@/` alias.
- Matches `__tests__/**/*.spec.js`. Coverage is off.
- `jest-setup.js` registers BootstrapVue and mocks `$t`.

**The 11 specs**
- Utilities components: Alert, Button, ButtonDashed, Modal, MultipleCheckboxInput.
- Utils: address, arrayFromNumber, arrayIsEqual, authListener, calculateTax, capitalizeFirstLetter.

**Actual coverage**
- 5 of 604 components, 0 of 269 pages, 6 of 45 utils.
- No tests for the store, mixins, or plugins.
- No CI job runs the tests, and the Sonar step is commented out.

**Linting**
- ESLint: `eslint:recommended` + `vue/recommended` + `nuxt/recommended` + prettier.
- Many rules are downgraded to warnings, for example `vue/no-mutating-props`.
- Prettier: 4-space indent, no semicolons, single quotes, print width 100.
- husky pre-commit runs lint-staged; commit-msg runs commitlint (conventional).

## 19. Team workflow and conventions

**Branches and commits**
- Branches: `CU-<clickupId>_<Title-Words>` (sub-branches like `CU-<id>-01-foundation`).
- PRs merge **straight into `master`** as Bitbucket merge commits: `Merged in <branch> (pull request #NNNN)`.
- There are back-merges from master into feature branches.
- The `release/*` flow described in `README.md` is not used.
- Commits follow Conventional Commits (310 of 312 non-merge commits in the last 6 months).

**Activity, last 6 months**
- Most-changed folders: components (invoice, utilities, settings, admin, form), pages/settings,
  assets/style.
- Recent infrastructure changes:
  - Phosphor icon migration (Sept–Oct 2026)
  - ESLint config added (Aug 2026)
  - Userback replaced Featurebase (Aug 2026)
  - FullCalendar swap and jQuery removal (Jul 2026)
  - Jenkins updates (Sept and Oct 2026)

**Code conventions.** Each item is marked as confirmed in code or taken from `aio-pos/CLAUDE.md`.

| Convention | Status |
| --- | --- |
| Components are imported explicitly and aliased with an `App` prefix | Confirmed: about 450 `AppButton` imports, no auto-import |
| API calls live in Vuex actions | Confirmed: 1,132 calls in the store vs 11 in the UI |
| Toasts use `this.$root.$bvToast.toast(...)` | Confirmed: 737 calls |
| Money uses `toMoney` (a **default** export, not a named one) or `v-money` | Confirmed: `utils/toMoney.js:5`; `v-money` 505 uses |
| Dates use moment-timezone (`this.moment`) | Confirmed: 511 calls |
| Modals use `components/utilities/Modal.vue`, not `b-modal` | Confirmed: 250 imports vs 1 `<b-modal>` |
| Tables use `b-table`, often through the deep-imported `AppTable` | Confirmed: 178 `<b-table>` tags, 18 deep imports |
| Tooltips use `v-b-tooltip` | Confirmed: 600 uses. The `.hover.nofade` modifier is UNVERIFIED. |
| Icons are Phosphor `ph ph-*` | Confirmed: 1,511 uses (`aio-pos/CLAUDE.md` wrongly says Material Icons) |
| Option order `name, layout, head, transition, components, mixins, props, data, computed, watch, mounted, methods` | UNVERIFIED (from `aio-pos/CLAUDE.md`) |
| Colours come from SCSS variables, with no hex literals | UNVERIFIED and **not strict**: hex literals exist, e.g. `#141414` in `plugins/client.js` (toggle default) and in `nuxt.config.js` (loading bar) |
| File naming: components PascalCase, pages kebab-case, store / utils / mixins camelCase | UNVERIFIED (from `aio-pos/CLAUDE.md`); exceptions exist, e.g. `store/AIOPay.js`, `mixins/screen-size.js` |

## 20. Existing documentation: how far to trust it

| Source | Verdict |
| --- | --- |
| `aio-pos/docs/` (437 files; 242 carry an `AI METADATA` header, generated from `prompt.txt` / `component-prompt.txt`, mostly Jul–Aug 2025) | **Use with caution.** The per-page and per-component docs are detailed but about 15 months old. Several sections are **wrong**:<br>- build-deployment (node 14, Docker, nginx)<br>- plugins (an invented `ADYEN_CLIENT_KEY` and `store/stripe.js`)<br>- the WebSocket channels in api-integration<br>- the state-management action names (0 of 17 exist)<br>- the pages-routing README route list<br>- 91 files still reference Material Icons |
| `aio-pos/CLAUDE.md` (962 lines) | Mostly accurate on conventions. **Stale** on icons ("ALWAYS use Material Icons") and on the `toMoney` import style. Points to `../ai-tools/frontend-registry/...`, which **does not exist**. |
| `.github/copilot-instructions.md`, `.claude/agents/*` | An older subset of CLAUDE.md, and Nuxt 2-specific agents |
| `README.md` | Stale: says node 18, port 3000, references `*.example` config files that don't exist, and describes a release-branch flow that isn't used |

The rule for this workspace: treat all of the above as **evidence about the legacy app, not as
instructions**. Check anything that matters against the code.

## 21. Migration hotspot inventory

These are the Vue 2 and Nuxt 2 surfaces that will need work, measured at `341775157`. The list
records the size of each surface; it makes no decisions.

| Surface | Size | Notes |
| --- | --- | --- |
| bootstrap-vue rc.27 + Bootstrap 4 | `<b-*>` in 329 files, `v-b-tooltip` 600, `$bvToast` 737, 34 deep `node_modules` imports, BS4 utility classes in 633+ files | Vue 2 only; also the source of global toasts and tooltips |
| `@nuxtjs/auth` v4 | `$auth` in 130 files, `$auth.user` 259 references; cookie and localStorage key `auth._token.local` read directly in 3 places | Nuxt 2 only |
| `@nuxtjs/axios` | 1,132 calls in the store, plus `CancelToken` 75 / `isCancel` 48 in the UI | Nuxt 2 only |
| Vuex | 126 files, 25.6k lines, about 1,725 `map*` helper uses | |
| `asyncData` / `fetch` | 97 / 3 pages (all `fetch` use the legacy signature); 35 redirect-to-default-tab guards | |
| vee-validate 2 | about 150 files (`v-validate` 498, `errors.*` 855+, `$validator` 395); 13 custom rules | v4 has a different API |
| Route names | 155 `-index` literals and 262 `$route.name` reads; sidebar slugs come from the backend | A naming contract |
| Mixins | 105 files use them, plus 1 global `Vue.mixin` | |
| Global Vue API | `Vue.prototype._` and `.moment`, `Vue.filter`, 8 `Vue.directive` (Vue 2 hooks), 10 `Vue.component`, `Vue.config.warnHandler` | |
| Template and instance API | old `slot=` / `slot-scope=` 938 / 673 (mostly b-table); `.sync` 54; `$listeners` 5; `$children` 3; `$parent` 107; `$set` 62; `$delete` / `Vue.set` 5; `.native` 17; `$nuxt.$on` / `$emit` event bus (about 21 emitters); `beforeDestroy` / `destroyed` in 89 files; `truncate` filter 10; custom-component `v-model` (`value` / `input`) everywhere | |
| Vue 2-only libraries | vue-multiselect 2 (190), vue2-editor (12), vue2-google-maps (6), vuejs-datepicker, v-calendar 2, vuedraggable 2, vue-virtual-scroller 1, vue-carousel, vue-js-toggle-button (63), vue-slider-component, portal-vue (3), vue-chartjs 3 / chart.js 2, vue-lazyload (26), element-ui (7) | |
| Nuxt config | `build.extend` (Webpack), `publicRuntimeConfig`, `head` scripts, `loading`, `router.middleware`, local module `modules/integrations.js`, `app/router.scrollBehavior.js`, `nuxtServerInit`, `nuxt-basic-auth-module`, `@nuxtjs/sentry`, `@nuxtjs/laravel-echo` | |
| Styling | Bootstrap loaded twice, full element-ui CSS, CDN `@import`s, 121 hand-written variable imports, `::v-deep` 46, `.slide-enter` transition classes, silenced Sass deprecations | |
| Tests | Jest + VTU1 + vue-jest, 11 specs | |
| Static assets | `static/` (261 files), 4 head-script JS files | |

## 22. Known quirks, dead code, and risks

**Dead or unused code**
- `middleware/permission.js` and the `checkPermission` action.
- The `@nuxtjs/laravel-echo` `$echo` instance.
- `store/systemAlerts.initializeRealTimeListeners`.
- `vue-numeric`, the global `line-chart`, and the `lineBreak` filter.
- 3 mixins, several utils and constants with 0 users, IcoFont classes, and `pages/new-pages`.

**Bugs found while mapping**
- The `plugins/axios.js` URL-exclusion check never matches.
- `reports/old-aio-pay-payout-report/index.vue:68` checks the new report's route name, so its
  default-tab redirect never fires.
- `reports/index.vue:66` and `settings/index.vue:231` read `[0].id` without a check, so they crash
  when the navigation entry is missing.
- `this.$toast` in `store/reports/homeVisitSurveyReport.js` is never injected.
- Some actions never settle their promise.
- Dead links to `my-reports` and `directory-calendar`.

**Duplicate trees:** `inventory/transfer-inventory` vs `transfer-inventory/`,
`aio-pay-payout-report` vs `old-aio-pay-payout-report`, `wholesale` vs `wholesale-management`.

**SSR hazards**
- `moment.tz.setDefault` runs in `created`, so it changes the moment default for the whole server
  process.
- Many browser-only libraries depend on `ssr:false` plugins, `<client-only>`, or `process.client`.

**Behaviour to preserve**
- Single-session enforcement (403 plus a force modal).
- Cross-tab reload when the token changes.
- Hard reloads after login, company switch, and location switch.
- The midnight reload.
- The concurrent-editor lock on routing.
- Forced logout over sockets.
- The token handoff between apps (`?token=`).

**Security notes**
- `registerToken` is exposed in public runtime config and compared on the client.
- Third-party IDs and tokens are hard-coded in `static/js/*` and `plugins/global.js`.
- Prod bakes `.env` into the Docker image.
- CI runs only a secrets scan.

---

## Appendix A — how to re-measure

Run these from any directory. The shell is zsh, so quote globs and keep path lists inline. `rg`
respects `.gitignore`. If `rg` hangs, it is reading stdin: append `< /dev/null`.

```sh
SHA=$(git -C ~/Work/aio-pos rev-parse --short HEAD); echo $SHA
cd ~/Work/aio-pos
find pages -name '*.vue' | wc -l                                   # pages
find components -name '*.vue' | wc -l                              # components
find store -name '*.js' | wc -l                                    # store files
rg -l --glob '*.vue' '^\s*(async\s+)?asyncData\s*\(' pages | wc -l  # asyncData pages
rg -l --glob '*.{vue,js}' '<b-[a-z]' . | wc -l                     # bootstrap-vue tag files
rg -o --glob '*.{vue,js}' 'v-b-tooltip' . | wc -l                  # tooltips
rg -l --glob '*.{vue,js}' '\$auth' . | wc -l                       # $auth files
rg -U --count-matches '\$axios\s*\.\$?(get|post|put|delete|patch)\(' store \
  | awk -F: '{s+=$2} END{print s}'                                 # store HTTP calls (multiline; don't pipe -U -o to wc -l)
rg -o --glob '*.{vue,js}' 'v-validate' . | wc -l                   # vee-validate directives
rg -l --glob '*.vue' '^\s*mixins:\s*\[' . | wc -l                  # files using mixins
rg -o --no-filename --glob '*.{vue,js}' "from ['\"][@~]/components/[^'\"]+['\"]" . \
  | sort | uniq -c | sort -rn | head -20                           # most-imported components
```
