#!/usr/bin/env python3
"""
Facebook Ads Library - Web Scraper Version
Não precisa de token especial - raspa a interface web pública
Uso: python3 fb_ads_scraper.py --keyword "curso online" --country BR --max-ads 20
"""

import sys
import os
import json
import argparse
import asyncio
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urlencode

# Add project to path
sys.path.insert(0, '/tmp/fb-ads-mcp')

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


class FacebookAdsScraper:
    """Scraper da Facebook Ads Library Web (pública)"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://www.facebook.com/ads/library"

    def _build_search_url(self, keyword: str, country: str = "BR",
                          ad_type: str = "all", active_status: str = "active") -> str:
        """Constrói URL de busca"""
        params = {
            'q': keyword,
            'type': ad_type,
            'active_status': active_status,
            'country': country.upper(),
            'sort_data[direction]': 'desc',
            'sort_data[mode]': 'relevancy_monthly_grouped',
            'media_type': 'all'
        }
        return f"{self.base_url}/?{urlencode(params)}"

    async def search_ads(self, keyword: str, country: str = "BR",
                         max_ads: int = 20, scroll_pause: float = 2.0) -> dict:
        """Busca anúncios por palavra-chave"""

        url = self._build_search_url(keyword, country)

        # Schema para extrair dados dos cards de anúncio
        schema = {
            "name": "ads",
            "baseSelector": "[data-testid='ad-library-card']",
            "fields": [
                {"name": "ad_id", "selector": "[data-testid='ad-library-card-id']", "type": "text"},
                {"name": "page_name", "selector": "[data-testid='ad-library-card-page-name']", "type": "text"},
                {"name": "page_id", "selector": "[data-testid='ad-library-card-page-id']", "type": "text"},
                {"name": "ad_text", "selector": "[data-testid='ad-library-card-body-text']", "type": "text"},
                {"name": "ad_headline", "selector": "[data-testid='ad-library-card-headline']", "type": "text"},
                {"name": "ad_cta", "selector": "[data-testid='ad-library-card-cta']", "type": "text"},
                {"name": "ad_image", "selector": "[data-testid='ad-library-card-image'] img", "type": "attribute", "attribute": "src"},
                {"name": "ad_video", "selector": "[data-testid='ad-library-card-video']", "type": "attribute", "attribute": "src"},
                {"name": "start_date", "selector": "[data-testid='ad-library-card-start-date']", "type": "text"},
                {"name": "platforms", "selector": "[data-testid='ad-library-card-platforms']", "type": "text"},
                {"name": "impressions", "selector": "[data-testid='ad-library-card-impressions']", "type": "text"},
                {"name": "spend", "selector": "[data-testid='ad-library-card-spend']", "type": "text"},
                {"name": "snapshot_link", "selector": "a[href*='ads/library/']", "type": "attribute", "attribute": "href"}
            ]
        }

        extraction_strategy = JsonCssExtractionStrategy(schema)

        config = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
            wait_for="[data-testid='ad-library-card']",
            scroll_delay=scroll_pause,
            max_scroll_count=5,
            page_timeout=60000
        )

        async with AsyncWebCrawler(config=BrowserConfig(headless=self.headless)) as crawler:
            result = await crawler.arun(url, config=config)

            if not result.success:
                return {"error": result.error_message, "success": False, "keyword": keyword}

            ads = result.extracted_content if result.extracted_content else []

            # Se extração falhar, tentar parsing manual do HTML
            if not ads and result.cleaned_html:
                ads = self._parse_html_manual(result.cleaned_html, keyword, country)

            # Limitar resultados
            ads = ads[:max_ads]

            return {
                "keyword": keyword,
                "country": country,
                "total_found": len(ads),
                "ads": ads,
                "search_url": url,
                "scraped_at": datetime.now().isoformat(),
                "success": True
            }

    def _parse_html_manual(self, html: str, keyword: str, country: str) -> List[Dict]:
        """Parsing manual fallback do HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        ads = []

        # Tentar vários seletores possíveis
        cards = soup.select("[data-testid='ad-library-card']") or \
                soup.select("div[role='article']") or \
                soup.select(".x1yztbdb")

        for card =0 for card in cards:
            ad = {}
            try:
                # Page name
                page_elem = card.select_one("[data-testid='ad-library-card-page-name'], a[href*='facebook.com/']")
                ad['page_name'] = page_elem.get_text(strip=True) if page_elem else ""

                # Ad text
                text_elem = card.select_one("[data-testid='ad-library-card-body-text'], .x193iq5w")
                ad['ad_text'] = text_elem.get_text(strip=True) if text_elem else ""

                # Headline
                head_elem = card.select_one("[data-testid='ad-library-card-headline'], .x1lliihq")
                ad['ad_headline'] = head_elem.get_text(strip=True) if head_elem else ""

                # Image
                img_elem = card.select_one("img[src*='fbcdn.net'], img[src*='scontent']")
                ad['ad_image'] = img_elem.get('src', '') if img_elem else ""

                # Start date
                date_elem = card.select_one("[data-testid='ad-library-card-start-date']")
                ad['start_date'] = date_elem.get_text(strip=True) if date_elem else ""

                # Platforms
                plat_elem = card.select_one("[data-testid='ad-library-card-platforms']")
                ad['platforms'] = plat_elem.get_text(strip=True) if plat_elem else ""

                # Impressions
                imp_elem = card.select_one("[data-testid='ad-library-card-impressions']")
                ad['impressions'] = imp_elem.get_text(strip=True) if imp_elem else ""

                # Spend
                spend_elem = card.select_one("[data-testid='ad-library-card-spend']")
                ad['spend'] = spend_elem.get_text(strip=True) if spend_elem else ""

                # Snapshot link
                link_elem = card.select_one("a[href*='ads/library/']")
                ad['snapshot_link'] = link_elem.get('href', '') if link_elem else ""

                if ad.get('page_name') or ad.get('ad_text'):
                    ad['keyword'] = keyword
                    ad['country'] = country
                    ads.append(ad)

            except Exception as e:
                continue

        return ads

    async def discover_brands(self, industry_keywords: str, country: str = "BR",
                              min_ads: int = 5, max_brands: int = 20) -> dict:
        """Descobre marcas por palavras-chave do setor"""
        keywords = [k.strip() for k in industry_keywords.split(",")]
        all_brands = {}

        for keyword in keywords:
            print(f"  Buscando: {keyword}...")
            result = await self.search_ads(keyword, country, max_ads=50)

            if not result.get("success"):
                continue

            for ad in result.get("ads", []):
                page_name = ad.get("page_name", "").strip()
                if not page_name:
                    continue

                key = page_name.lower()
                if key not in all_brands:
                    all_brands[key] = {
                        "page_name": page_name,
                        "keywords_matched": [],
                        "ad_count": 0,
                        "sample_ads": []
                    }
                all_brands[key]["keywords_matched"].append(keyword)
                all_brands[key]["ad_count"] += 1
                if len(all_brands[key]["sample_ads"]) < 3:
                    all_brands[key]["sample_ads"].append({
                        "text": ad.get("ad_text", "")[:100],
                        "headline": ad.get("ad_headline", "")[:100],
                        "image": ad.get("ad_image", ""),
                        "start_date": ad.get("start_date", ""),
                        "platforms": ad.get("platforms", ""),
                        "impressions": ad.get("impressions", ""),
                        "spend": ad.get("spend", "")
                    })

        # Filtrar e ordenar
        filtered = [
            v for v in all_brands.values()
            if v["ad_count"] >= min_ads
        ]
        filtered.sort(key=lambda x: x["ad_count"], reverse=True)

        return {
            "industry_keywords": industry_keywords,
            "country": country,
            "total_brands_found": len(filtered),
            "brands": filtered[:max_brands],
            "success": True
        }

    async def get_brand_ads(self, brand_name: str, country: str = "BR",
                            max_ads: int = 30) -> dict:
        """Busca todos os anúncios de uma marca específica"""
        result = await self.search_ads(brand_name, country, max_ads=max_ads)

        if not result.get("success"):
            return result

        ads = result.get("ads", [])

        # Filtrar apenas anúncios dessa marca
        brand_ads = [ad for ad in ads if brand_name.lower() in ad.get("page_name", "").lower()]

        # Análise básica
        platforms = {}
        total_impressions = 0
        total_spend = 0

        for ad in brand_ads:
            for p in ad.get("platforms", "").split(", "):
                if p:
                    platforms[p] = platforms.get(p, 0) + 1

            # Tentar extrair números
            imp_text = ad.get("impressions", "")
            spend_text = ad.get("spend", "")

            # Parse impression range (ex: "1M - 2M")
            imp_match = re.search(r'[\d,.]+[KM]?', imp_text.replace(',', ''))
            if imp_match:
                val = imp_match.group()
                if 'K' in val:
                    total_impressions += float(val.replace('K', '')) * 1000
                elif 'M' in val:
                    total_impressions += float(val.replace('M', '')) * 1000000
                else:
                    total_impressions += float(val)

            spend_match = re.search(r'[\d,.]+[KM]?', spend_text.replace(',', ''))
            if spend_match:
                val = spend_match.group()
                if 'K' in val:
                    total_spend += float(val.replace('K', '')) * 1000
                elif 'M' in val:
                    total_spend += float(val.replace('M', '')) * 1000000
                else:
                    total_spend += float(val)

        return {
            "brand": brand_name,
            "country": country,
            "total_ads": len(brand_ads),
            "estimated_impressions": int(total_impressions),
            "estimated_spend": int(total_spend),
            "platforms_distribution": platforms,
            "ads": brand_ads,
            "success": True
        }

    async def compare_brands(self, brands: List[str], country: str = "BR",
                             max_ads_per_brand: int = 20) -> dict:
        """Compara múltiplas marcas"""
        results = {}
        for brand in brands:
            print(f"  Analisando: {brand}...")
            results[brand] = await self.get_brand_ads(brand, country, max_ads_per_brand)

        return {
            "brands": brands,
            "country": country,
            "comparison": results,
            "success": True
        }

    def export_to_csv(self, data: dict, filename: str) -> str:
        """Exporta para CSV"""
        import csv

        ads = data.get("ads", [])
        if not ads:
            return "Erro: nenhum anúncio para exportar"

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'keyword', 'page_name', 'ad_headline', 'ad_text',
                'ad_image', 'start_date', 'platforms',
                'impressions', 'spend', 'snapshot_link',
                'scraped_at'
            ])

            for ad in ads:
                writer.writerow([
                    ad.get("keyword", ""),
                    ad.get("page_name", ""),
                    ad.get("ad_headline", ""),
                    ad.get("ad_text", "")[:500],
                    ad.get("ad_image", ""),
                    ad.get("start_date", ""),
                    ad.get("platforms", ""),
                    ad.get("impressions", ""),
                    ad.get("spend", ""),
                    ad.get("snapshot_link", ""),
                    data.get("scraped_at", "")
                ])

        return f"Exportado {len(ads)} anúncios para {filename}"

    def generate_report(self, niche: str, brands: List[str],
                        comparison: dict, country: str = "BR") -> dict:
        """Gera relatório de inteligência"""
        report = {
            "niche": niche,
            "country": country,
            "generated_at": datetime.now().isoformat(),
            "brands_analyzed": len(brands),
            "summary": {},
            "top_insights": [],
            "recommendations": [],
            "brand_details": {}
        }

        total_ads = 0
        total_spend = 0
        all_platforms = set()

        for brand, data in comparison.get("comparison", {}).items():
            if data.get("success"):
                brand_ads = data.get("total_ads", 0)
                brand_spend = data.get("estimated_spend", 0)
                brand_platforms = data.get("platforms_distribution", {})

                total_ads += brand_ads
                total_spend += brand_spend
                all_platforms.update(brand_platforms.keys())

                report["brand_details"][brand] = {
                    "total_ads": brand_ads,
                    "estimated_spend": brand_spend,
                    "platforms": brand_platforms,
                    "top_ads": data.get("ads", [])[:5]
                }

        report["summary"] = {
            "total_ads_analyzed": total_ads,
            "estimated_total_market_spend": total_spend,
            "avg_ads_per_brand": total_ads / len(brands) if brands else 0,
            "platforms_found": list(all_platforms)
        }

        report["top_insights"] = [
            f"Mercado '{niche}' com {total_ads} anúncios ativos entre {len(brands)} marcas no {country}",
            f"Gasto estimado total: ~R$ {total_spend:,.0f}" if country == "BR" else f"Gasto estimado total: ~${total_spend:,.0f}",
            f"Plataformas ativas: {', '.join(all_platforms)}",
            f"Média de {total_ads/len(brands):.0f} anúncios por marca"
        ]

        report["recommendations"] = [
            "🎯 Foque em Reels/Stories (maior alcance orgânico no Brasil)",
            "💬 Use CTA direto para WhatsApp (maior conversão BR)",
            "🎁 Ofereça lead magnet (PDF, checklist, mini-curso grátis)",
            "💰 Teste oferta low-ticket R$ 27-97 (PIX/boleto no copy)",
            "📱 Estrutura CBO: 3 Ad Sets (LAL 1% + Interesses + Broad)",
            "⏰ Horários pico BR: 12h-14h e 19h-22h",
            "🔄 Roteiro: Gancho → Dor → Solução → Prova → CTA WhatsApp",
            "📊 Comece R$ 50-100/dia por ad set, escale 20% a cada 3 dias"
        ]

        return report


async def main():
    parser = argparse.ArgumentParser(description="Facebook Ads Library - Web Scraper (sem token)")
    parser.add_argument("--keyword", help="Palavra-chave para buscar anúncios")
    parser.add_argument("--country", default="BR", help="Código do país (padrão: BR)")
    parser.add_argument("--max-ads", type=int, default=20, help="Máx anúncios (padrão: 20)")
    parser.add_argument("--discover", help="Palavras-chave para descobrir marcas (ex: 'curso online,ebook')")
    parser.add_argument("--min-ads", type=int, default=5, help="Mínimo de anúncios para discover")
    parser.add_argument("--brand", help="Nome da marca para análise profunda")
    parser.add_argument("--compare", help="Marcas para comparar (separadas por vírgula)")
    parser.add_argument("--export", help="Arquivo CSV para exportar")
    parser.add_argument("--report", help="Nicho para gerar relatório (use com --compare)")
    parser.add_argument("--headless", action="store_true", default=True, help="Modo headless (padrão: True)")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Mostrar browser")

    args = parser.parse_args()

    scraper = FacebookAdsScraper(headless=args.headless)

    if args.discover:
        print(f"\n🔍 Descobrindo marcas para: {args.discover} no {args.country}")
        result = await scraper.discover_brands(args.discover, args.country, args.min_ads)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.brand:
        print(f"\n🔎 Analisando marca: {args.brand} no {args.country}")
        result = await scraper.get_brand_ads(args.brand, args.country, args.max_ads)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if args.export and result.get("success"):
            print(f"\n📤 Exportando para CSV...")
            msg = scraper.export_to_csv(result, args.export)
            print(msg)

    elif args.compare:
        brands = [b.strip() for b in args.compare.split(",")]
        print(f"\n📊 Comparando {len(brands)} marcas: {brands}")
        result = await scraper.compare_brands(brands, args.country, args.max_ads)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if args.report:
            print(f"\n📋 Gerando relatório para: {args.report}")
            report = scraper.generate_report(args.report, brands, result, args.country)
            print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.keyword:
        print(f"\n🔎 Buscando anúncios: '{args.keyword}' no {args.country}")
        result = await scraper.search_ads(args.keyword, args.country, args.max_ads)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if args.export and result.get("success"):
            print(f"\n📤 Exportando para CSV...")
            msg = scraper.export_to_csv(result, args.export)
            print(msg)

    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())