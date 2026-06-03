import asyncio
import json
import os
from playwright.async_api import async_playwright
import httpx

async def capture():
    if not os.path.exists("screenshots"): os.makedirs("screenshots")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        base_url = "http://127.0.0.1:8000"

        # Login Page
        print("Navigating to login page...")
        try:
            await page.goto(base_url, timeout=10000)
            await asyncio.sleep(2)
            await page.screenshot(path="screenshots/login.png")
            print("Captured login.png")
        except Exception as e:
            print(f"Failed to capture login: {e}")

        roles = ["ADMIN", "SELLER", "CASHIER", "STOREKEEPER", "WORKER"]
        role_to_page = {
            "ADMIN": "manager",
            "SELLER": "seller",
            "CASHIER": "cashier",
            "STOREKEEPER": "storekeeper",
            "WORKER": "worker"
        }

        for role in roles:
            username = role.lower() if role != "ADMIN" else "admin"
            password = f"{username}123"
            print(f"Logging in as {role}...")

            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(f"{base_url}/auth/login", data={"username": username, "password": password})
                    if resp.status_code != 200:
                        print(f"Auth failed for {username}: {resp.status_code}")
                        continue
                    token = resp.json()["access_token"]
                    resp = await client.get(f"{base_url}/inventory/me", headers={"Authorization": f"Bearer {token}"})
                    user = resp.json()

                await page.goto(base_url)
                await page.evaluate(f"localStorage.setItem('access_token', '{token}')")
                await page.evaluate(f"localStorage.setItem('user', '{json.dumps(user)}')")

                target_url = f"{base_url}/dashboard/{role_to_page[role]}"
                print(f"Navigating to {target_url}...")
                await page.goto(target_url)
                await asyncio.sleep(3)
                await page.screenshot(path=f"screenshots/{role_to_page[role]}.png")
                print(f"Captured {role_to_page[role]}.png")
            except Exception as e:
                print(f"Error capturing {role}: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
