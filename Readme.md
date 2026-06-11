# ezPawnPal — Appium Automation Framework

A robust, Page Object Model (POM) based Appium automation suite for the ezPawnPal Android application. This framework handles full end-to-end flows including login, item counting (jewelry, firearms, electronics, watches), barcode scanning, and location assignments.

---

## 📱 1. Device & App Configuration

The tests are currently configured to run on the following physical device setup:

| Field | Value |
| --- | --- |
| **UDID** | `R9ZR505QC8L` |
| **Model** | Samsung SM-T500 (gta4lwifi) |
| **App Package** | `com.ezpawnpal` |
| **Launcher Activity** | `.SplashActivity` |
| **Main Activity** | `.MainActivity` (after splash) |
| **Home Screen Label** | ezPawnPal |

*Note: Capabilities live in `ezpawnpal.json`. Use this exact same JSON in the Appium Inspector (Remote → paste capabilities).*

---

## 📂 2. Project Layout

Capabilities JSON, `pages/`, `tests/`, and `xmlFiles/` (for Inspector dumps) make up the core structure.

```text
pages/
  common/          appium_wait.py, adb_helper.py, barcode_14401.png
  login/           login_page.py, home_page.py
  itemCount/       item_count_page.py, itemrecount_page.py, firearms_page.py, etc.
  itemLocator/     item_locator_page.py, label_location_assign.py, etc.
  item_manager/    item_manager_page.py, barcode_scan_page.py, barcode_decode.py
  refresh/         refresh_data_page.py

tests/
  test_suite.py      Default Appium flow (one session, 15 tests)
  shared_session.py  Login-once driver setup & safe teardown reset
  refresh_data/      refresh_data.py (long sync — run via run_refresh_test.py)
  runner_utils.py    Results table for run_tests / run_refresh_test

```

---

## 🛠️ 3. Environment Setup & Installation

**1. Clone and setup the Python virtual environment:**

```bash
cd ~/impressico-projects/ezPawnPal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

**2. Permanently Set Android Environment Variables:**
To ensure Appium and ADB commands always work, add the Android SDK paths to your `.bashrc` profile:

```bash
echo 'export ANDROID_HOME="$HOME/Android/Sdk"' >> ~/.bashrc
echo 'export ANDROID_SDK_ROOT="$HOME/Android/Sdk"' >> ~/.bashrc
echo 'export PATH="$ANDROID_HOME/platform-tools:$PATH"' >> ~/.bashrc
source ~/.bashrc

```

**3. Verify the Device:**
Ensure the tablet is plugged in and USB debugging is enabled.

```bash
adb devices -l
# Expect: R9ZR505QC8L    device ...

```

---

## 🚀 4. Starting the Server & Inspector (Terminal 1)

**Start Appium:**
Open a dedicated terminal to run the Appium server using `npx`:

```bash
npx appium

```

*Leave this terminal window open and running in the background.*

**Launch Appium Inspector:**
Appium Inspector is used to capture XML files and UI images from the live app. This is crucial for getting element details (IDs, XPaths, classes) to manipulate the UI and create/update page objects for future test cases.

```bash
cd ~/Downloads
./Appium-Inspector-2026.2.1-linux-x86_64.AppImage --no-sandbox

```

* Remote connection → `http://127.0.0.1:4723`
* Load capabilities from `ezpawnpal.json`
* Save page sources under `xmlFiles/`

---

## ▶️ 5. Running the Tests (Terminal 2)

Open a second terminal, ensure your virtual environment is **active**, and use our CLI runners to execute tests. Appium must already be running in Terminal 1.

```bash
cd ~/impressico-projects/ezPawnPal
source .venv/bin/activate

```

### Main Suite Commands (`run_tests.py`)

Run the master "Happy Path" suite. All tests execute in **one app session** (it logs in once, and uses the hamburger menu to navigate between modules).

| Command | Target Test |
| --- | --- |
| `python run_tests.py login` | `test_01_login_and_store_location_setup` |
| `python run_tests.py sync` | `test_02_post_login_home_or_data_sync` |
| `python run_tests.py item_count` | `test_03_item_count_layout_and_buttons` |
| `python run_tests.py locator` | `test_04_item_locator_layout_and_buttons` |
| `python run_tests.py barcode` | `test_05_retail_item_manager_live_barcode_scan` |
| `python run_tests.py assign` | `test_06_assign_item_location` |
| `python run_tests.py setup` | `test_07_setup_location_change` |
| `python run_tests.py label` | `test_08_label_confimation` |
| `python run_tests.py recount` | `test_09_item_count_jewelry_recount` |
| `python run_tests.py item4recount` | `test_10_item_count_closing_attempt4_recount` |
| `python run_tests.py firearms` | `test_11_item_count_firearms_recount` |
| `python run_tests.py elec` | `test_12_item_count_electronics_recount` |
| `python run_tests.py elec4` | `test_13_item_count_electronics_attempt4_recount` |
| `python run_tests.py pw` | `test_14_item_count_pw_recount` |
| `python run_tests.py pw4` | `test_15_item_count_pw_attempt4_recount` |
| `python run_tests.py` | **(Default)** Runs all 15 tests sequentially |

### Master Execution

```bash
# Run everything sequentially via unittest tables
python run_all.py

# Run everything and generate an Allure HTML report
python run_all_allure.py
allure serve ./allure-results

```

---

## 🔍 6. Specific Module Overviews

### Barcode Module (Layout + Store 14401 Details)

To run the barcode test directly via `unittest` (ensure you use the project venv):

```bash
.venv/bin/python3 -m unittest tests.item_manager.barcode_scan_test -v

```

**Changing the Scanned Item:** The physical barcode image is stored at `pages/common/barcode_14401.png` (store 14401 item `144010051344`). Replace this image file to change the scanned item ID without needing to edit the test code!

### Error-Path Tests (`run_error_tests.py`)

Excluded from `run_tests.py` because they intentionally use invalid credentials, wrong barcodes, and trigger wrong-store modals.

```bash
python run_error_tests.py              # all error tests
python run_error_tests.py login        # login errors (employee, password, IP)
python run_error_tests.py barcode      # Retail Item Manager wrong barcode
python run_error_tests.py assign       # Assign Item Location wrong barcode
python run_error_tests.py --list

```

### Refresh Data / Long Tests (`run_refresh_test.py`)

Excluded from `run_tests.py` because each sync can take **5–15+ minutes**.

```bash
python run_refresh_test.py              # menu UI + MDM refresh + Item Locations refresh
python run_refresh_test.py menu         # account menu UI only (accountlogo.xml)
python run_refresh_test.py mdm          # Product MDM only
python run_refresh_test.py locations    # Item Locations only
python run_refresh_test.py --list

```

**Data Sync Flow Details:**
Both syncs follow this path: `home` → `profile menu` → `refresh action` → `Yes` → `wait for Downloaded` → `Close` → `home`.

* **MDM Confirm Dialog:** *"Refresh Product MDM Data?"* → `PRODUCT MDM DATA` → `Downloaded`
* **Locations Confirm Dialog:** *"Refresh Item Locations?"* → `ITEM LOCATIONS` → `Downloaded`

**Optional Timeout Overrides:**
If the syncs are taking longer than the default 900 seconds (15 mins), you can override them via ENV variables:

```bash
EZPAWNPAL_MDM_REFRESH_TIMEOUT=1200 python run_refresh_test.py mdm
EZPAWNPAL_LOCATIONS_REFRESH_TIMEOUT=1200 python run_refresh_test.py locations

```