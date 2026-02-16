import { test, expect } from '@playwright/test';

test('waveform and spectrum render and handle resizing', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Wait for loading
  await page.waitForTimeout(2000);

  // Take a baseline screenshot
  await page.screenshot({ path: '/home/jules/verification/v4_baseline.png' });

  // Simulate some scrolling/zooming interaction
  const waveform = page.locator('canvas').first();
  const box = await waveform.boundingBox();
  if (box) {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    // rapid zooming
    for (let i = 0; i < 10; i++) {
        await page.mouse.wheel(0, -100);
        await page.waitForTimeout(50);
    }
  }

  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/home/jules/verification/v4_after_interaction.png' });

  // Verify elements are still there
  await expect(page.locator('canvas')).toHaveCount(3);
});
