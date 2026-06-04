#!/usr/bin/env bash
# Quick device + ezPawnPal identity (run with USB debugging on).
set -euo pipefail
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Android/Sdk}"
export PATH="$ANDROID_HOME/platform-tools:$PATH"

echo "=== adb devices ==="
adb devices -l

SERIAL="${ANDROID_SERIAL:-$(adb devices | awk '/\tdevice$/{print $1; exit}')}"
if [[ -z "${SERIAL}" ]]; then
  echo "No device attached." >&2
  exit 1
fi

echo ""
echo "=== Device (${SERIAL}) ==="
adb -s "$SERIAL" shell getprop ro.product.manufacturer
adb -s "$SERIAL" shell getprop ro.product.model

PKG=com.ezpawnpal
echo ""
echo "=== ${PKG} ==="
adb -s "$SERIAL" shell cmd package resolve-activity --brief "$PKG" || true
echo ""
echo "=== Current focus (open ${PKG} first for best result) ==="
adb -s "$SERIAL" shell dumpsys window | grep -E 'mCurrentFocus|mFocusedApp' || true
