import os
import time
import urllib.request
import json
from playwright.sync_api import sync_playwright

def post_json(url, data):
    payload = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        return resp.read()

def generate():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1200, 'height': 800})

        # 1. Start by loading the app
        page.goto("http://127.0.0.1:8000")
        time.sleep(2)

        # 2. Load the audio file via API
        audio_path = os.path.abspath("tests/data/Test.mp3")
        oscope_path = audio_path + ".oscope"
        if os.path.exists(oscope_path):
            os.remove(oscope_path)

        post_json("http://127.0.0.1:8000/project/open", {"path": audio_path})
        time.sleep(2) # Wait for processing

        # 3. Take main UI screenshot
        # Add some flags and lyrics first
        page.evaluate("window.useStore.setState({ lyrics: [], flags: [], harmony_flags: [] })")
        page.evaluate("window.useStore.getState().setShowLyrics(true)")
        page.evaluate("window.useStore.getState().addFlag(1.0)")
        page.evaluate("window.useStore.getState().addHarmonyFlag(2.0, {r: 'G', ca: '', q: 'm', ext: '7', alt: [], add: [], b: '', ba: ''})")
        page.evaluate("window.useStore.getState().addLyric({s: 'Wavoscope', t: 1.5, l: 1.0})")
        time.sleep(1)

        # Screenshot: Main View
        page.screenshot(path="docs/images/main_view.png")

        # 4. Screenshot: Lyrics Track Detail
        # Focus on the lyrics/waveform area
        lyrics_track = page.locator(".relative.w-full.h-8.select-none.bg-surface")
        lyrics_track.screenshot(path="docs/images/lyrics_track.png")

        # 5. Screenshot: Spectrum with Filter
        # Enable filter handles
        page.evaluate("window.useStore.getState().updateFilter({low_enabled: true, high_enabled: true, low_hz: 300, high_hz: 800})")
        time.sleep(1)

        # Focus on spectrum
        spectrum = page.locator(".flex-1.min-h-0").last
        spectrum.screenshot(path="docs/images/spectrum_filter.png")

        # 6. Screenshot: Settings Dialog
        # Set it in the store FIRST so the dialog picks it up when opened
        time.sleep(0.5)
        page.evaluate("window.useStore.getState().setShowSettings(true)")
        time.sleep(1)
        # Switch to Recovery tab to show the new category
        # Since the tabs are buttons in a flex container, we can find it by text
        page.locator("button:has-text('Recovery')").click()
        time.sleep(1)
        page.locator(".fixed.inset-0").screenshot(path="docs/images/settings_dialog.png")

        # 7. Screenshot: Rhythm Flag Dialog
        page.evaluate("window.useStore.getState().setShowSettings(false)")
        page.evaluate("window.useStore.getState().setEditingFlagIdx(0)")
        time.sleep(1)
        # Use a more specific locator if possible, but .fixed.inset-0 is the dialog backdrop
        page.locator(".fixed.inset-0 > div").screenshot(path="docs/images/rhythm_dialog.png")

        # 8. Screenshot: Harmony Flag Dialog
        page.evaluate("window.useStore.getState().setEditingFlagIdx(null)")
        page.evaluate("window.useStore.getState().setEditingHarmonyFlagIdx(0)")
        time.sleep(1)
        page.locator(".fixed.inset-0 > div").screenshot(path="docs/images/harmony_dialog.png")

        browser.close()

if __name__ == "__main__":
    generate()
