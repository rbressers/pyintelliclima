# Adding Support for New IntelliClima Devices

This guide explains how to capture the network traffic of the official **IntelliClima+**
Android app so that new device types (such as the ECOCOMFORT 3.0) can be reverse-engineered
and added to this library.

You do **not** need programming experience to follow this guide, but it's definitely helpful if you have some Linux (commandline) experience. What you do need is a Linux
computer (Ubuntu is recommended) and an IntelliClima account with a device that is not yet
supported.

---

## How This Works

`pyintelliclima` communicates with the IntelliClima cloud API. Because IntelliClima does not
publish a public API, the only way to discover how a new device type works is to watch what
the official app sends to and receives from the cloud. This technique is called
**traffic interception** or a **man-in-the-middle proxy**.

The tool we use for this is [mitmproxy](https://mitmproxy.org/), a free and open-source proxy
that lets you inspect HTTPS traffic. We run the IntelliClima+ app inside
[Waydroid](https://waydro.id/), a layer that lets you run Android apps natively on Linux,
and route all app traffic through mitmproxy.

This approach works because of two things the IntelliClima+ app does not protect against.
First, it does not use **certificate pinning** — a technique where an app refuses to trust
any certificate except its own server's, which would make mitmproxy invisible to it. By
installing mitmproxy's certificate into Android's trusted store (step 5), the app accepts
mitmproxy as a legitimate go-between without noticing. Second, the API sends and receives
plain **JSON** — human-readable text — rather than encrypting or obfuscating the message
bodies beyond the standard HTTPS connection. Once mitmproxy decrypts the connection, the
requests and responses can be read directly. The developer could have protected against both
of these, which would make this kind of reverse engineering significantly harder or
impossible.

This guide is based on the blog post
[**"Use a Proxy with Waydroid"** by Julien Duponchelle](https://julien.duponchelle.info/android/use-proxy-with-waydroid/),
which explains the general setup process in detail. The steps below are adapted specifically
for capturing IntelliClima+ traffic.

---

## Prerequisites

- A computer running **Ubuntu** (22.04 or later recommended) with a **Wayland** desktop session
  (see below).
- An internet connection.
- An **IntelliClima account** with the device you want to add support for already paired in the
  official app.

### Getting a Wayland Session on Ubuntu

Waydroid requires Wayland, which is Ubuntu's modern display system. On Ubuntu 22.04 and later,
Wayland is the default, but it is easy to accidentally be on the older X11 session instead.

**Check which session you are using:**
Click the clock or the top-right system tray area, click your username or the power icon, and
look at the top of the screen after you log in. Alternatively, open a terminal and run:

```bash
echo $XDG_SESSION_TYPE
```

If the output is `wayland`, you are already on a Wayland session and can skip the rest of
this section. If it says `x11`, follow the steps below.

**Switch to a Wayland session:**

1. Log out of your current session (click the top-right system tray → your username → Log Out).
2. On the login screen, click your username but **do not enter your password yet**.
3. Look for a small **gear icon** in the bottom-right corner of the screen and click it.
4. A menu appears with options such as "Ubuntu", "Ubuntu on Wayland", and "Ubuntu on Xorg".
   Select **"Ubuntu"** or **"Ubuntu on Wayland"**.
5. Enter your password and log in. You are now on Wayland.

**If you do not see a gear icon or a Wayland option**, one of the following is likely the cause:

- **Wrong display manager.** The gear icon only appears when Ubuntu's default login manager
  (`gdm3`) is in use. Some Ubuntu variants ship with a different one (`lightdm`) that does not
  offer Wayland. Install and activate `gdm3`:
  ```bash
  sudo apt install gdm3
  ```
  During installation you may be prompted to choose a default display manager — select `gdm3`.
  Then reboot. The gear icon should now appear at the login screen.

- **Wayland is disabled in the GDM configuration.** This can happen on some systems after
  an upgrade. Open the configuration file:
  ```bash
  sudo nano /etc/gdm3/custom.conf
  ```
  Find the line that reads `#WaylandEnable=false` or `WaylandEnable=false` and change it to:
  ```ini
  WaylandEnable=true
  ```
  Save the file (`Ctrl+O`, then `Ctrl+X`), then reboot.

---

## Step 1: Install Waydroid and ADB

Waydroid lets you run Android apps on your Linux desktop. Follow the official installation
instructions for Ubuntu/Debian here:
[https://docs.waydro.id/usage/install-on-desktops#ubuntu-debian-and-derivatives](https://docs.waydro.id/usage/install-on-desktops#ubuntu-debian-and-derivatives)

After installation, search for "Waydroid" in your application menu and launch it. You will be
prompted to download an Android image. Choose the option **without** Google apps — you only
need the base Android system.

You also need **ADB** (Android Debug Bridge), a tool for sending commands to the Android
container. Install it with:

```bash
sudo apt install adb -y
```

---

## Step 2: Install mitmproxy

mitmproxy is the tool that will intercept and display the app's network requests. Install it
with:

```bash
sudo apt install mitmproxy -y
```

---

## Step 3: Install the IntelliClima+ App in Waydroid

The easiest way is to install the app directly from the **Google Play Store** inside Waydroid.
If you chose to include Google apps when setting up Waydroid, the Play Store will already be
available. Log in with a Google account, search for **"IntelliClima+"** (by Fantini Cosmi),
and install it as you would on a phone.

If you did not include Google apps, or the Play Store is not working, you can sideload the APK
as an alternative:

1. Download the **IntelliClima+** APK from a trusted APK mirror such as
   [APKPure](https://apkpure.com) or [APKCombo](https://apkcombo.com). Search for
   "IntelliClima+" (by Fantini Cosmi).
2. Install it into Waydroid by running:
   ```bash
   waydroid app install /path/to/intelliclima.apk
   ```
   Replace `/path/to/intelliclima.apk` with the actual path to the downloaded file
   (for example `~/Downloads/intelliclima.apk`).

Once installed, launch Waydroid and verify the IntelliClima+ app appears. Do **not** log in
yet.

---

## Step 4: Find Your Waydroid Network Address

mitmproxy needs to listen on the network interface that Waydroid uses. Run:

```bash
ip address show waydroid0
```

You will see output similar to this:

```
18: waydroid0: <BROADCAST,MULTICAST,UP,LOWER_UP> ...
    inet 192.168.240.1/24 ...
```

Note the IP address after `inet` — in this example it is `192.168.240.1`. Yours may differ.
Use your actual address in the commands below wherever `192.168.240.1` appears.

---

## Step 5: Install the mitmproxy Certificate in Waydroid

The IntelliClima+ app uses HTTPS. For mitmproxy to read HTTPS traffic, Android must trust
its certificate. This is a one-time setup.

**5a.** Start mitmproxy once briefly (just to generate the certificate files):

```bash
mitmweb -p 8888 --listen-host 192.168.240.1
```

Wait a few seconds, then stop it with `Ctrl+C`.

**5b.** Get the certificate hash:

```bash
openssl x509 -subject_hash_old -in ~/.mitmproxy/mitmproxy-ca-cert.pem
```

The first line of the output is the hash, for example `a8990c1d`. Note your hash — it will
be different from this example.

**5c.** Install the certificate into Waydroid's trusted certificate store. Replace `a8990c1d`
with your actual hash from the previous step:

```bash
sudo mkdir -p /var/lib/waydroid/overlay/system/etc/security/cacerts/
sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem \
    /var/lib/waydroid/overlay/system/etc/security/cacerts/a8990c1d.0
sudo chmod 644 /var/lib/waydroid/overlay/system/etc/security/cacerts/a8990c1d.0
```

> The filename must be your hash followed by `.0` — do not change the extension.

**5d.** Restart Waydroid to apply the certificate:

```bash
sudo systemctl restart waydroid-container
```

---

## Step 6: Start Capturing Traffic

Now you will route Waydroid's traffic through mitmproxy and use the IntelliClima+ app normally.

**6a.** Tell Waydroid to route its traffic through mitmproxy:

```bash
adb shell settings put global http_proxy "192.168.240.1:8888"
```

**6b.** Start Waydroid and mitmproxy. You can either start them together in one terminal:

```bash
waydroid & mitmweb -p 8888 --listen-host 192.168.240.1
```

Or open two terminal windows and start each separately — Waydroid from the application menu
and mitmproxy with:

```bash
mitmweb -p 8888 --listen-host 192.168.240.1
```

mitmproxy will open a web interface in your browser at `http://127.0.0.1:8081`. Keep this
tab open — this is where you will see captured requests.

**6c.** Launch the **IntelliClima+** app inside Waydroid and log in with your IntelliClima
credentials. Use the app normally for a few minutes. Specifically, make sure to:
- Open the device list (so the app fetches device status)
- Change the speed or mode of your device at least once
- If your device has any special features (timers, programs, sensors), interact with those too

You should see requests appearing in the mitmproxy browser tab at `http://127.0.0.1:8081`.

---

## Step 7: Export the Captured Traffic

Once you have captured a good set of interactions, export the traffic log for sharing.

**7a.** In the mitmproxy web interface (`http://127.0.0.1:8081`), click **File → Save** in the
menu bar. This saves a `.mitm` file (for example `flows.mitm`) to your Downloads folder.
This file contains the full captured traffic.

> Alternatively, you can also export individual requests as a HAR file using
> **File → Export → HAR**.

**7b.** Before sharing, open the `.mitm` file to check for sensitive information (see the
next section).

**7c.** When done, remove the proxy setting from Waydroid so normal app use is restored:

```bash
adb shell settings put global http_proxy :0
```

---

## Step 8: What to Check Before Sharing Your Logs

> **You are solely responsible for what you share.** The maintainer of this project accepts
> no responsibility for any personal or account information accidentally included in shared
> logs. Before sharing, you must review and remove all personal information yourself.

**No personal or account information should remain in the file.** This includes at minimum:

- Your **username and email address**
- Your **password hash** (the login request to `/user/login/` contains a SHA-256 hash of
  your password — remove or replace this entire request)
- Your **account ID** and **device serial numbers**
- Any other value that could identify you or your account

Use the mitmproxy web interface (`http://127.0.0.1:8081`) to review each captured request
before exporting. You can delete individual requests from the list by selecting them and
pressing `d`. Export only after you are satisfied nothing personal remains.

Additionally, **change your IntelliClima password** in the official app after capturing,
regardless of whether you believe the log is clean. This ensures any credentials that may
have slipped through are no longer valid.

**Inspecting the exported file before sharing:**

You can re-open the exported `.mitm` file in mitmproxy at any time — without needing
Waydroid or an active proxy — to review exactly what it contains, the same way the
maintainer would when receiving it:

```bash
mitmweb -r /path/to/flows.mitm
```

This opens the mitmproxy web interface at `http://127.0.0.1:8081` with all the saved
requests loaded. Click through each request and check both the **Request** and **Response**
tabs for any personal information. If you find something that should be removed, close
mitmweb, reopen the original capture session (`mitmweb -r /path/to/flows.mitm`), delete
the offending request by clicking it and pressing `d`, then re-export with **File → Save**.

---

## Step 9: Share Your Logs with the Maintainer

Open a new GitHub issue on this repository and attach the exported `.mitm` (or `.har`) file.
Please include the following information in the issue:

- Your **device model** (for example: IntelliClima ECOCOMFORT 3.0)
- A short description of **what actions you performed** in the app while capturing
  (for example: "logged in, checked device status, set fan speed to medium, set auto mode"). Be very specific here in exactly what steps you took, and in what order. Otherwise it's very difficult to know which request corresponds to which action.
- Your **operating system** (Ubuntu version)
- Whether HTTPS traffic was successfully captured or only HTTP (if you only see HTTP requests,
  the certificate installation may not have worked — try restarting Waydroid and repeating
  step 6)

The more interactions you capture (especially changing different settings and modes), the
more complete the protocol picture will be, and the easier it is to implement support.

**GitHub Issues:** [https://github.com/dvdinth/pyintelliclima/issues](https://github.com/dvdinth/pyintelliclima/issues)

---

## Troubleshooting

**mitmproxy browser tab shows no requests from IntelliClima+**
- Make sure you ran the `adb shell settings put global http_proxy` command *after* starting
  mitmproxy and *before* opening the app.
- Confirm the IP address in the `adb` command matches the one from `ip address show waydroid0`.
- Try restarting Waydroid with `sudo systemctl restart waydroid-container` and repeating
  step 6.

**IntelliClima+ shows a connection error or certificate error**
- The certificate installation (step 5) may not have worked. Confirm the file exists:
  ```bash
  ls /var/lib/waydroid/overlay/system/etc/security/cacerts/
  ```
  You should see a file named `<your-hash>.0`. If not, repeat step 5.
- Make sure you restarted Waydroid after installing the certificate.

**`adb` command says "no devices found"**
- Waydroid must be running before you use `adb`. Launch Waydroid from the application menu
  first, then try again.

**Waydroid does not start / says Wayland is required**
- Follow the "Getting a Wayland Session on Ubuntu" steps in the Prerequisites section above.
