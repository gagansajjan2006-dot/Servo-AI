from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Listen for console events
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        
        # Listen for page errors
        page.on("pageerror", lambda err: print(f"ERROR: {err.message}"))
        
        print("Navigating to http://127.0.0.1:8000")
        try:
            page.goto("http://127.0.0.1:8000")
            page.wait_for_timeout(2000) # Wait 2 seconds for JS to execute
        except Exception as e:
            print(f"Exception: {e}")
            
        browser.close()

if __name__ == '__main__':
    run()
