import { test, expect } from '@playwright/test';

test('lyrics transcription interaction flow', async ({ page }) => {
    // Navigate to the app (mocking backend response if needed, but here we assume it's running)
    await page.goto('http://localhost:5173');

    // Force loaded state
    await page.evaluate(() => {
        window.useStore.setState({
            loaded: true,
            showLyrics: true,
            lyrics: []
        });
    });

    const canvas = page.locator('canvas.cursor-crosshair');
    await expect(canvas).toBeVisible();

    // 1. Single click to add lyric
    const box = await canvas.boundingBox();
    if (box) {
        await page.mouse.click(box.x + 50, box.y + 16);
    }

    // Verify input appeared
    const input = page.locator('input[type="text"]');
    await expect(input).toBeVisible();

    // 2. Type "He" and then "-"
    await input.fill('He');
    await page.keyboard.press('-');

    // The current one should be committed as "He" and a new one should appear.
    // Wait for the new input (it should still be visible because a new one was created)
    await expect(input).toBeVisible();

    // Check state
    const lyrics = await page.evaluate(() => window.useStore.getState().lyrics);
    expect(lyrics.length).toBe(2);
    expect(lyrics[0].text).toBe('He');

    // 3. Type "llo" and " " (space)
    await input.fill('llo');
    await page.keyboard.press(' ');

    const lyrics2 = await page.evaluate(() => window.useStore.getState().lyrics);
    expect(lyrics2.length).toBe(3);
    expect(lyrics2[1].text).toBe('llo');

    // 4. Test L key (outside input)
    await page.keyboard.press('Escape'); // Finish editing
    await expect(input).not.toBeVisible();

    await page.keyboard.press('l');
    const lyrics3 = await page.evaluate(() => window.useStore.getState().lyrics);
    expect(lyrics3.length).toBe(4);
});
