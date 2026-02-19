from playwright.sync_api import sync_playwright, expect
import time
import os

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        print("Navigating to app...")
        # Try both common ports
        try:
            page.goto("http://localhost:5173", timeout=5000)
        except:
            page.goto("http://localhost:5174", timeout=5000)

        time.sleep(5)

        print("Mocking store state with SHORT NAMES...")
        page.evaluate("""
            window.useStore.setState({
                loaded: true,
                filename: 'Test.mp3',
                harmony_flags: [{t: 0.5, c: {r: 'D', ca: '#', q: 'm', ext: '7', alt: ['b5'], add: [], b: '', ba: ''}}]
            })
        """)

        print("Opening Harmony Dialog...")
        page.evaluate("window.useStore.getState().setEditingHarmonyFlagIdx(0)")

        time.sleep(2)

        screenshot_path = "/home/jules/verification/chord_dialog_final.png"
        os.makedirs("/home/jules/verification", exist_ok=True)
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        # Check text field
        val = page.locator("input").first.evaluate("el => el.value")
        print(f"Chord notation: {val}")
        assert val == "D#m7b5"

        browser.close()

if __name__ == "__main__":
    import subprocess
    backend = subprocess.Popen(["python3", "backend/main.py"], env={**os.environ, "PYTHONPATH": "."})
    frontend = subprocess.Popen(["npm", "run", "dev"], cwd="frontend")

    time.sleep(10)

    try:
        run_verification()
    finally:
        backend.terminate()
        frontend.terminate()
