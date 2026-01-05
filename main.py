import os
import asyncio
from fastapi import FastAPI
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "MasterGMB Online", "engine": "Playwright-Stealth-V4"}

@app.get("/analyze")
async def analyze(niche: str, location: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled" # Esconde que é robô
            ]
        )
        # Fingerprint de humano real
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            search_query = f"{niche} em {location}"
            url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            # Vai para o Google Maps
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Tenta clicar no botão "Aceitar tudo" dos cookies (comum na Europa/servidores)
            try:
                cookie_button = page.locator('button:has-text("Aceitar tudo"), button:has-text("Accept all")')
                if await cookie_button.is_visible():
                    await cookie_button.click()
            except:
                pass

            # Espera os resultados (seletor dos cards de empresa)
            # O Google usa vários seletores, tentamos os mais comuns
            await page.wait_for_selector('div[role="article"]', timeout=20000)
            
            listings = await page.query_selector_all('div[role="article"]')
            competitors = []

            for listing in listings[:5]:
                try:
                    name = await listing.get_attribute('aria-label')
                    if not name:
                        # Fallback se o aria-label falhar
                        title_el = await listing.query_selector('.qBF1Pd')
                        name = await title_el.inner_text()
                    
                    competitors.append({
                        "name": name,
                        "reviews": ["Análise de gap processando...", "Destaque: Localização"]
                    })
                except:
                    continue

            await browser.close()
            return {
                "status": "success",
                "data": {
                    "niche": niche,
                    "location": location,
                    "competitors": competitors
                }
            }

        except Exception as e:
            if 'browser' in locals(): await browser.close()
            return {"status": "error", "message": f"Erro na raspagem: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
