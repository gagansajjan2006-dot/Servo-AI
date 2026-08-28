import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        errors = []
        page.on("console", lambda msg: errors.append(f"CONSOLE: {msg.type} {msg.text}"))
        page.on("pageerror", lambda exc: errors.append(f"PAGE ERROR: {exc}"))
        
        page.goto("http://127.0.0.1:8000")
        
        try:
            page.wait_for_selector("text=Timetable Food Plan", timeout=3000)
            page.click("text=Timetable Food Plan")
            page.wait_for_timeout(2000)
            
            # Take a screenshot to see what's rendered
            page.screenshot(path="timetable_tab_screenshot.png")
            print("Screenshot saved to timetable_tab_screenshot.png")
            
            # Also check display style
            res = page.evaluate('''() => {
                const el = document.getElementById('view-timetable');
                return {
                    isActive: el.classList.contains('active'),
                    display: window.getComputedStyle(el).display,
                    htmlLength: el.innerHTML.length
                };
            }''')
            print("EVAL RESULT:", res)
        except Exception as e:
            errors.append(f"ERROR: {e}")
            
        print("Captured Logs:")
        for err in errors:
            print(err)
            
        browser.close()

if __name__ == "__main__":
    run()
