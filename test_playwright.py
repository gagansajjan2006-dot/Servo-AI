import asyncio
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Listen for console events
        page.on("console", lambda msg: print(f"CONSOLE {msg.type}: {msg.text}"))
        # Listen for page errors
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        print("Visiting http://127.0.0.1:8000/")
        await page.goto("http://127.0.0.1:8000/")
        
        await page.wait_for_timeout(2000)
        
        # Click the menu tab
        print("Clicking menu tab...")
        await page.click("#tab-menu")
        
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot.png")
        print("Screenshot saved to screenshot.png")
        await browser.close()

asyncio.run(main())
