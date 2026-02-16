import os
import time
import requests
from playwright.sync_api import sync_playwright

def generate():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1200, 'height': 800})

        # 1. Start by loading the app
        page.goto("http://127.0.0.1:8000")
        time.sleep(2)

        # 2. Load the audio file via API
        audio_path = os.path.abspath("tests/Test.mp3")
        requests.post("http://127.0.0.1:8000/project/open", json={"path": audio_path})
        time.sleep(2) # Wait for processing

        # 3. Take main UI screenshot
        # Add some flags first
        page.evaluate("window.useStore.getState().addFlag(1.0)")
        page.evaluate("window.useStore.getState().addHarmonyFlag(2.0, {root: 'G', accidental: '', quality: 'm', extension: '7', alterations: [], additions: [], bass: '', bass_accidental: ''})")
        time.sleep(1)

        # Screenshot: Main View
        page.screenshot(path="docs/images/main_view.png")

        # 4. Screenshot: Spectrum with Filter
        # Enable filter
        page.evaluate("window.useStore.getState().updateFilter({enabled: true, low_hz: 300, high_hz: 3000})")
        time.sleep(1)

        # Focus on spectrum
        spectrum = page.locator(".flex-1.min-h-0").last
        spectrum.screenshot(path="docs/images/spectrum_filter.png")

        # 5. Screenshot: Settings Dialog
        # Set it in the store FIRST so the dialog picks it up when opened
        page.evaluate("window.useStore.getState().updateConfig({high_quality_enhancement: true})")
        time.sleep(0.5)
        page.evaluate("window.useStore.getState().setShowSettings(true)")
        time.sleep(1)
        page.locator(".fixed.inset-0").screenshot(path="docs/images/settings_dialog.png")

        # 6. Screenshot: Flag Dialog
        page.evaluate("window.useStore.getState().setShowSettings(false)")
        page.evaluate("window.useStore.getState().setEditingFlagIdx(0)")
        time.sleep(1)
        page.locator(".fixed.inset-0").screenshot(path="docs/images/flag_dialog.png")

        browser.close()

if __name__ == "__main__":
    generate()
