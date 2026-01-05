import os
import asyncio
from fastapi import FastAPI
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "MasterGMB Online"}

@app.get("/analyze")
async def analyze(niche: str, location: str):
    async with async_playwright() as p:
        # Launching browser with settings for Railway
        browser = await p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        search_query = f"{niche} em {location}"
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        
        try:
            # Aumentamos o timeout para 60 segundos para evitar bugs de lentidão
            await page.goto(url, timeout=60000)
            await page.wait_for_selector('.Nv2Ybe', timeout=15000)
            
            listings = await page.query_selector_all('.Nv2Ybe')
            competitors = []

            # Coletamos os Top 5
            for listing in listings[:5]:
                try:
                    name_raw = await listing.inner_text()
                    clean_name = name_raw.split('\n')[0]
                    
                    # Clicar para pegar reviews (Gap Analysis)
                    await listing.click()
                    await page.wait_for_timeout(2000)
                    review_elements = await page.query_selector_all('.MyE63c')
                    reviews = [await r.inner_text() for r in review_elements[:3]]

                    competitors.append({
                        "name": clean_name,
                        "reviews": reviews
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
            await browser.close()
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # O Railway usa a variável de ambiente PORT automaticamente
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
