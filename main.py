import os
import asyncio
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "MasterGMB Online", "engine": "Docker-Playwright"}

@app.get("/analyze")
async def analyze(niche: str, location: str):
    if not niche or not location:
        return {"status": "error", "message": "Nicho e Localização são obrigatórios"}

    async with async_playwright() as p:
        try:
            # Lançando o browser - No Docker ele já sabe onde o executável está
            browser = await p.chromium.launch(
                headless=True, 
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            search_query = f"{niche} em {location}"
            url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            # Navega até o Google Maps
            await page.goto(url, timeout=60000)
            
            # Espera pelos resultados (seletor de cards do Google Maps)
            try:
                await page.wait_for_selector('.Nv2Ybe', timeout=15000)
            except:
                pass

            listings = await page.query_selector_all('.Nv2Ybe')
            competitors = []

            # Extrai os Top 5
            for listing in listings[:5]:
                try:
                    name_raw = await listing.inner_text()
                    clean_name = name_raw.split('\n')[0]
                    
                    # Clica para abrir detalhes e pegar reviews (opcional para Gap Analysis)
                    await listing.click()
                    await page.wait_for_timeout(1500)
                    
                    # Pega as 3 primeiras reviews visíveis
                    review_elements = await page.query_selector_all('.MyE63c')
                    reviews = []
                    for rev in review_elements[:3]:
                        txt = await rev.inner_text()
                        if txt: reviews.append(txt)

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
            if 'browser' in locals(): await browser.close()
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Pega a porta do Railway ou usa 8080 como padrão
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
