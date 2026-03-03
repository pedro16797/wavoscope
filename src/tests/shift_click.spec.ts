import { test, expect } from '@playwright/test';
import * as path from 'path';

test('shift-click rhythm flag adds new flag at correct interval', async ({ page }) => {
  page.on('console', msg => console.log('BROWSER:', msg.text()));
  await page.goto('http://127.0.0.1:8000');

  // Load audio
  const audioPath = '/app/src/tests/data/Test.mp3';
  await page.evaluate(async (path) => {
    const res = await fetch('/project/open', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path })
    });
    if (!res.ok) throw new Error("Failed to open project");
  }, audioPath);

  // Wait for load
  await expect(async () => {
    const status = await page.evaluate(() => (window as any).useStore.getState().loaded);
    expect(status).toBe(true);
  }).toPass({ timeout: 10000 });

  // Add two flags via store for precise positioning
  await page.evaluate(async () => {
    const store = (window as any).useStore.getState();
    await store.addFlag(1.0);
    await store.addFlag(3.0);
  });

  // Wait for flags to be added
  await expect(async () => {
    const flags = await page.evaluate(() => (window as any).useStore.getState().flags);
    expect(flags.length).toBe(2);
  }).toPass();

  const flagsBefore = await page.evaluate(() => (window as any).useStore.getState().flags);
  console.log('Flags before click:', JSON.stringify(flagsBefore));

  // Now Shift-click the second flag (at 3.0s)
  const zoom = await page.evaluate(() => (window as any).useStore.getState().zoom);
  const offset = await page.evaluate(() => (window as any).useStore.getState().offset);
  const x = (3.0 - offset) * zoom;

  const timeline = page.locator('.h-10.w-full.border-b.select-none.cursor-crosshair canvas');
  const box = await timeline.boundingBox();
  if (!box) throw new Error("No timeline box");

  await page.screenshot({ path: 'tests/click_target.png' });

  // Click on the timeline canvas
  await page.keyboard.down('Shift');
  await page.mouse.click(box.x + x, box.y + box.height / 2);
  await page.keyboard.up('Shift');

  // Verify third flag at 5.0s (3.0 + (3.0 - 1.0))
  await expect(async () => {
    const flags = await page.evaluate(() => (window as any).useStore.getState().flags);
    // It might take a moment to update via fetchStatus
    if (flags.length < 3) throw new Error("Flag not added yet");
    expect(flags.length).toBe(3);
    expect(flags[2].t).toBeCloseTo(5.0, 1);
  }).toPass({ timeout: 5000 });
});
