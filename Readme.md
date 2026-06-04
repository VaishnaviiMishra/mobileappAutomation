# ezPawnPal — Appium automation

Capabilities JSON, `pages/`, `tests/`, and `xmlFiles/` for Inspector dumps.

## Project layout

```
pages/
  common/          appium_wait.py, adb_helper.py
  login/           login_page.py, home_page.py
  itemCount/       item_count_page.py
  itemLocator/     item_locator_page.py
  common/          appium_wait.py, adb_helper.py, barcode_14401.png
  item_manager/    item_manager_page.py, barcode_scan_page.py, barcode_decode.py

tests/
  test_suite.py      default Appium flow (one session, 9 tests)
  shared_session.py  login-once driver setup
  refresh_data/      refresh_data.py (long sync — run via run_refresh_test.py)
  runner_utils.py    results table for run_tests / run_refresh_test

pages/refresh/       refresh_data_page.py
```

## Device and app (already resolved on your tablet)

| Field | Value |
|--------|--------|
| **UDID** | `R9ZR505QC8L` |
| **Model** | Samsung **SM-T500** (`gta4lwifi`) |
| **appPackage** | `com.ezpawnpal` |
| **Launcher activity** | `.SplashActivity` |
| **Main activity** (after splash) | `.MainActivity` |
| **Home screen label** | `ezPawnPal` |

Capabilities live in [`ezpawnpal.json`](ezpawnpal.json). Use the same JSON in **Appium Inspector** (Remote → paste capabilities).

## One-time Python setup

```bash
cd ~/impressico-projects/ezPawnPal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Terminal: Android + Appium

**Terminal 1 — Appium**

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export ANDROID_SDK_ROOT="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
appium
```

**Verify device**

```bash
adb devices -l
# Expect: R9ZR505QC8L    device ...
```

**Appium Inspector**

```bash
~/Downloads/Appium-Inspector-2026.2.1-linux-x86_64.AppImage --no-sandbox
```

1. Remote connection → `http://127.0.0.1:4723`
2. Load capabilities from `ezpawnpal.json`
3. Save page source under `xmlFiles/`

## Run tests

**Terminal 2 — project venv** (Appium must already be running)

```bash
cd ~/impressico-projects/ezPawnPal
source .venv/bin/activate
python run_tests.py
```

| Command | Test |
|---------|------|
| `python run_tests.py login` | `test_01_login_and_store_location_setup` |
| `python run_tests.py home` | `test_02_post_login_home_or_data_sync` |
| `python run_tests.py item_count` | `test_03_item_count_layout_and_buttons` |
| `python run_tests.py item_locater` | `test_04_item_locator_layout_and_buttons` |
| `python run_tests.py barcode` | `test_05_retail_item_manager_live_barcode_scan` |
| `python run_tests.py assign` | `test_06_assign_item_location` |
| `python run_tests.py setup_location` | `test_07_setup_location_change` |
| `python run_tests.py label_confimation` | `test_08_label_confimation` |
| `python run_tests.py recount` | `test_09_item_count_jewelry_recount` |
| `python run_tests.py` (default) | All 9 tests in **one app session** (login once; hamburger between tests) |
| `python run_tests.py all` | Same as default |

**Run everything (unittest tables):**

```bash
python run_all.py
```

**Run everything (Allure HTML report):**

```bash
python run_all_allure.py
allure serve ./allure-results
```

Barcode module (layout + store 14401 details) — **use the project venv**, not system `python3`:

```bash
.venv/bin/python3 -m unittest tests.item_manager.barcode_scan_test -v
```

Or: `source .venv/bin/activate` then `python3 -m unittest tests.item_manager.barcode_scan_test -v`

Barcode image: `pages/common/barcode_14401.png` (store 14401 item `144010051344`). Replace it to change the scanned item ID without editing test code.

## Refresh data (long tests)

Excluded from `run_tests.py` because each sync can take **5–15+ minutes**.

```bash
python run_refresh_test.py              # menu UI + MDM refresh + Item Locations refresh
python run_refresh_test.py menu           # account menu UI only (accountlogo.xml)
python run_refresh_test.py mdm           # Product MDM only
python run_refresh_test.py locations    # Item Locations only
python run_refresh_test.py --list
```

Optional timeout overrides (seconds, default `900` each):

```bash
EZPAWNPAL_MDM_REFRESH_TIMEOUT=1200 python run_refresh_test.py mdm
EZPAWNPAL_LOCATIONS_REFRESH_TIMEOUT=1200 python run_refresh_test.py locations
```

## Error-path tests

Excluded from `run_tests.py` (invalid credentials, wrong barcodes, wrong-store modals).

```bash
python run_error_tests.py              # all error tests
python run_error_tests.py login        # login errors (employee, password, IP)
python run_error_tests.py barcode      # Retail Item Manager wrong barcode
python run_error_tests.py assign       # Assign Item Location wrong barcode
python run_error_tests.py --list
```

| Flow | Confirm dialog | Data Sync section |
|------|----------------|-------------------|
| **Refresh Product MDM Data** | “Refresh Product MDM Data?” | PRODUCT MDM DATA → Downloaded |
| **Refresh Item Locations Data** | “Refresh Item Locations?” | ITEM LOCATIONS → Downloaded |

Both: home → profile menu → refresh action → **Yes** → wait for **Downloaded** → **Close** → home.
