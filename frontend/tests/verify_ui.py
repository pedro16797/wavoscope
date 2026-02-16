from playwright.sync_api import expect, sync_playwright
import time
import subprocess
import os
import signal

def test_ui_basic():
    # Start backend
    print("Starting backend...")
    backend_proc = subprocess.Popen(["python3", "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(3) # Wait for backend to start

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://127.0.0.1:8000")

            # Check for title/elements
            print("Checking UI elements...")
            expect(page.get_by_text("Spectrum Analyzer")).to_be_visible()
            expect(page.get_by_text("Ready to load audio")).to_be_visible()

            # Check settings dialog
            print("Checking settings dialog...")
            # The gear icon is the last button in the PlaybackBar
            page.locator("button").last.click()
            expect(page.get_by_text("Settings", exact=True)).to_be_visible()
            page.get_by_role("button", name="Cancel").click()

            print("UI test passed!")
        finally:
            browser.close()
            # Stop backend
            os.kill(backend_proc.pid, signal.SIGTERM)

if __name__ == "__main__":
    test_ui_basic()
