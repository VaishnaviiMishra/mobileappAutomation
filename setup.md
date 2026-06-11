#  The Ultimate Beginner's Guide: Setting Up Mobile Automation

Welcome! If you are new to mobile automation, this guide is for you. We are going to set up your computer so it can automatically tap, swipe, and type inside an Android app, just like a human would.

To do this, we need to build a "bridge" between your code and the phone. Here are the tools we will install to build that bridge:

1. **VS Code & Python:** Where we write our code.
2. **Android Studio & Emulator:** A fake "virtual phone" that runs on your computer screen.
3. **Appium:** The robot brain that translates our Python code into phone taps.
4. **Appium Inspector:** A magnifying glass that helps us find the hidden IDs of buttons on the phone screen.

Let's build it step-by-step!

---

## 🛠️ Phase 1: The Coding Environment (VS Code & Python)

First, we need a place to write code and the language to write it in.

### 1. Install VS Code

1. Go to the [Visual Studio Code website](https://code.visualstudio.com/).
2. Download and install it for your computer.
3. Open VS Code, click on the **Extensions** icon (four squares on the left menu), search for **Python**, and click **Install**.

### 2. Install Python & Set Up a Virtual Environment (`venv`)

A virtual environment (`venv`) is like a sandbox. It keeps all the code packages for this specific project safely inside the project folder so they don't mess up your computer.

1. Open VS Code.
2. Go to `File > Open Folder` and select your project folder (e.g., `ezPawnPal`).
3. Open a terminal inside VS Code by clicking `Terminal > New Terminal` at the top.
4. Type this command to create the sandbox:
```bash
python3 -m venv .venv

```


5. Now, **activate** the sandbox. You must do this every time you open the project!
```bash
source .venv/bin/activate

```


*(You will know it worked if you see `(.venv)` at the beginning of your terminal line).*
6. Finally, install the tools our code needs:
```bash
pip install -r requirements.txt

```



---

## 🤖 Phase 2: The Robot Brain (Node.js & Appium)

Appium is the engine that drives the automation, but Appium is built using a language called Node.js. We need to install Node first.

### 1. Install Node.js

1. Go to the [Node.js website](https://nodejs.org/).
2. Download and install the **LTS (Long Term Support)** version.
3. To check if it worked, open a terminal and type:
```bash
node -v

```


*(It should print a version number like `v18.x.x`)*

### 2. Install Appium

Now that Node is installed, it gave us a tool called `npm` (Node Package Manager). We will use `npm` to download Appium.

1. In your terminal, type:
```bash
npm install -g appium

```


2. Appium needs a specific "driver" to understand Android devices. Install the Android driver by typing:
```bash
appium driver install uiautomator2

```



---

## 📱 Phase 3: The Virtual Phone (Android Studio)

We need a phone to test on! Instead of using a real physical tablet, we will create a fake one on your screen called an **Emulator**.

### 1. Install Android Studio

1. Go to the [Android Studio website](https://developer.android.com/studio) and download it.
2. Run the installer. **Important:** When it asks what components to install, make sure **Android SDK** and **Android Virtual Device (AVD)** are checked!

### 2. Set Up Environment Variables (The Magic Paths)

Your computer needs to know exactly where Android Studio installed its secret tools.

1. Open a terminal and open your computer's settings file by typing:
```bash
nano ~/.bashrc

```


2. Use your arrow keys to scroll to the very bottom, and paste these exactly:
```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export ANDROID_SDK_ROOT="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/platform-tools:$PATH"

```


3. Press `Ctrl + O`, then `Enter` to save. Press `Ctrl + X` to exit.
4. Tell your computer to reload the settings:
```bash
source ~/.bashrc

```



### 3. Create the Emulator

1. Open **Android Studio**.
2. Click on **More Actions** (or the 3 dots) and select **Virtual Device Manager**.
3. Click **Create Device**.
4. Choose a device (e.g., `Pixel 6` or a Tablet) and click **Next**.
5. Download a System Image (this is the Android version, like Android 13/Tiramisu). Click the **Download** arrow next to it, wait for it to finish, select it, and click **Next**.
6. Name your device and click **Finish**.
7. Click the **Play (▶)** button next to your new device. A virtual phone will appear on your screen!

### 4. Find the Device Name

We need to tell Appium the name of this virtual phone.

1. In your terminal, type:
```bash
adb devices

```


2. You should see something like:
```text
emulator-5554    device

```


3. `emulator-5554` is your device's name (UDID). Open your `ezpawnpal.json` file in VS Code and make sure the `"udid": "emulator-5554"` matches!

---

## 🔍 Phase 4: The X-Ray Glasses (Appium Inspector)

Appium Inspector lets us look "inside" the app to find the exact names of buttons (like `loginButton`) so our code knows what to click.

### 1. Download Appium Inspector

1. Go to the [Appium Inspector Releases page](https://github.com/appium/appium-inspector/releases).
2. Download the version for your computer (if you are on Linux, get the `.AppImage` file).

### 2. How to use it

1. First, make sure your Emulator is running and the ezPawnPal app is open on it.
2. Open a terminal and start the Appium server:
```bash
npx appium

```


3. Now, open **Appium Inspector** (on Linux, you run `./Appium-Inspector-xxxx.AppImage --no-sandbox`).
4. In the Inspector, there is a box for **JSON Representation**. Paste the contents of your `ezpawnpal.json` file into this box and click **Save**.
5. Click **Start Session**.
6. *Magic!* A screenshot of your emulator will appear. You can now click on any button on the screen, and the Inspector will tell you its ID on the right side!

---

## 🎬 Phase 5: How to Run the Tests Everyday

You are fully set up! Here is your daily routine whenever you want to run a test:

**Terminal 1: Start the Robot Brain**

1. Open a terminal.
2. Type `npx appium` and press Enter. (Leave this window alone).

**Terminal 2: Run the Code**

1. Open VS Code.
2. Open a new terminal inside VS Code.
3. Activate the sandbox: `source .venv/bin/activate`
4. Make sure your Emulator is running!
5. Tell Python to run the tests:
```bash
python run_tests.py

```



Sit back, don't touch your mouse, and watch the virtual phone click and type all by itself!