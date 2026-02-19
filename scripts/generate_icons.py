import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

def generate_icons():
    # Paths
    root_dir = Path(__file__).resolve().parent.parent
    svg_path = root_dir / "resources" / "icons" / "WavoscopeLogo.svg"
    output_dir = root_dir / "resources" / "icons"
    public_dir = root_dir / "frontend" / "public"

    if not svg_path.exists():
        print(f"Error: {svg_path} not found.")
        return

    sizes = [16, 32, 48, 64, 128, 256, 512]
    png_paths = {}

    print("Launching browser to render SVG...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{svg_path}")
        page.wait_for_selector("svg")
        page.evaluate("""
            const svg = document.querySelector('svg');
            if (svg) {
                svg.style.width = '100vw';
                svg.style.height = '100vh';
                svg.style.display = 'block';
                svg.style.margin = '0';
                svg.style.padding = '0';
            }
            if (document.body) {
                document.body.style.margin = '0';
                document.body.style.padding = '0';
                document.body.style.overflow = 'hidden';
            }
        """)
        for size in sizes:
            page.set_viewport_size({"width": size, "height": size})
            png_path = output_dir / f"temp_icon_{size}.png"
            page.screenshot(path=str(png_path), omit_background=True)
            png_paths[size] = png_path
        browser.close()

    # Create ICO file from the 256x256 PNG
    ico_path = output_dir / "app-icon.ico"
    img = Image.open(png_paths[256])
    img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Created {ico_path}, size: {os.path.getsize(ico_path)} bytes")

    # Create ICNS file for macOS
    icns_path = output_dir / "app-icon.icns"
    img_icns = Image.open(png_paths[512])
    img_icns.save(icns_path, format="ICNS")
    print(f"Created {icns_path}, size: {os.path.getsize(icns_path)} bytes")

    app_icon_png = output_dir / "app-icon.png"
    shutil.copy(png_paths[512], app_icon_png)

    if public_dir.exists():
        shutil.copy(ico_path, public_dir / "favicon.ico")
        shutil.copy(png_paths[32], public_dir / "favicon-32x32.png")
        shutil.copy(png_paths[512], public_dir / "favicon.png")
        shutil.copy(svg_path, public_dir / "favicon.svg")

    for path in png_paths.values():
        if path.exists():
            os.remove(path)

if __name__ == "__main__":
    generate_icons()
