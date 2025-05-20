import requests
import sys
from fastmcp import FastMCP
import os
#from dotenv import load_dotenv
#load_dotenv()

API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
if not API_KEY:
  raise RuntimeError("Brakuje CRYPTOPANIC_API_KEY w środowisku")

mcp = FastMCP("crypto news")
        
@mcp.tool()
def get_crypto_news(kind: str = "news", num_pages: int = 2) -> str:
  try:
      news = fetch_crypto_news(kind, num_pages)
      if not news:
          return "Nie pobrano żadnych wiadomości. Sprawdź klucz API i parametry."
      return concatenate_news(news)
  except Exception as e:
      # log do stderr, zwracając też komunikat klientowi
      print(f"[tool error] {e}", file=sys.stderr)
      # Możesz też zwrócić komunikat do klienta:
      return f"Wyjątek w narzędziu: {e}"

def fetch_crypto_news_page(kind: str, page: int): 
    url = "https://cryptopanic.com/api/v1/posts/"
    params = {
      "auth_token": API_KEY,
      "kind": kind,  # news, analysis, videos
      "regions": "en",
      "public": "true",  
      "page": page      
    }
    resp = requests.get(url, params=params)
    # debug do stderr, na stdout pójdzie tylko JSON‑RPC
    print(f"Fetching {resp.url} -> {resp.status_code}", file=sys.stderr)
    if resp.status_code != 200:
        print(f"[tool error] HTTP {resp.status_code}: {resp.text}", file=sys.stderr)
        return []
    data = resp.json()
    return data.get("results", [])
        
def fetch_crypto_news(kind: str = "news", num_pages: int = 10):
    all_news = []
    for page in range(1, num_pages + 1):
        # debug do stderr
        print(f"Fetching page {page}...", file=sys.stderr)
        items = fetch_crypto_news_page(kind, page)
        if not items:
              print(f"No more news on page {page}.", file=sys.stderr)
              break
        all_news.extend(items)
    return all_news        

def concatenate_news(news_items):
  concatenated_text = ""
  for idx, news in enumerate(news_items):  # łączenie wszystkich wiadomości
    title = news.get("title", "No Title")
    concatenated_text += f"- {title}\n"
       
  return concatenated_text.strip()


if __name__ == "__main__":
  # Test bez MCP, tylko sama funkcja
  print("TEST:", get_crypto_news("news", 1))
  # A potem uruchamiaj:
  mcp.run(transport="stdio")
