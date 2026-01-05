import os
import asyncio
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "MasterGMB Online"}

@app.get("/analyze")
async def analyze(niche: str, location: str):
    if not niche or not location:
        return {"status": "error", "message": "Nicho e Localização são obrigatórios"}

    async with async_playwright() as p:
        try:
            # Lançando o browser com as proteções do Railway
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
            
            print(f"Buscando: {url}") # Isso vai aparecer nos Logs do Railway
            
            await page.goto(url, timeout=60000)
            
            # Tenta esperar por um dos seletores do Google Maps
            try:
                await page.wait_for_selector('.Nv2Ybe', timeout=20000)
            except:
                # Se não achar o seletor, pode ser que o Google mudou. Pegamos o que tiver.
                print("Seletor principal não encontrado, tentando alternativa...")

            listings = await page.query_selector_all('.Nv2Ybe')
            competitors = []

            for listing in listings[:5]:
                try:
                    name_raw = await listing.inner_text()
                    clean_name = name_raw.split('\n')[0]
                    competitors.append({"name": clean_name})
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
            print(f"ERRO CRÍTICO: {str(e)}")
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
