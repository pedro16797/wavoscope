from playwright.sync_api import sync_playwright

def verify_resize():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Small window
        page.set_viewport_size({"width": 800, "height": 600})
        page.goto("http://127.0.0.1:8000")
        page.wait_for_timeout(1000)
        page.screenshot(path="resize_small.png")

        # Large window
        page.set_viewport_size({"width": 1200, "height": 800})
        page.wait_for_timeout(1000)
        page.screenshot(path="resize_large.png")

        browser.close()

if __name__ == "__main__":
    verify_resize()
