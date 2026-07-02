#!/usr/bin/env python3
"""
Wrapper direto para usar a Facebook Ads Library API sem MCP server.
Use direto no terminal: python fb_ads_direct.py --token SEU_TOKEN --brand "nike" --country BR
"""

import sys
import os
import json
import argparse
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio

# Add project to path
sys.path.insert(0, '/tmp/fb-ads-mcp')

from crawl4ai import AsyncWebCrawler, BrowserConfig


class FacebookAdsDirect:
    """Wrapper direto da Facebook Ads Library API"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v19.0/ads_archive"
        self.crawler = None

    def _make_request(self, params: dict) -> dict:
        params['access_token'] = self.access_token
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

    def search_ads(
        self,
        brand_name: str,
        country: str = "BR",
        ad_type: str = "ALL",
        date_range: int = 30,
        limit: int = 50
    ) -> dict:
        """Busca anúncios de uma marca"""
        params = {
            'search_terms': brand_name,
            'ad_reached_countries': [country],
            'fields': 'id,ad_creation_time,ad_creative_bodies,ad_creative_link_captions,ad_creative_link_descriptions,ad_creative_link_titles,ad_snapshot_url,currency,demographic_distribution,delivery_by_region,impressions,page_id,page_name,publisher_platforms,spend',
            'limit': limit,
            'ad_active_status': 'ALL'
        }

        if ad_type != "ALL":
            params['ad_type'] = ad_type

        result = self._make_request(params)

        if result.get("success") is False:
            return result

        return {
            "brand": brand_name,
            "total_ads": len(result.get("data", [])),
            "ads": result.get("data", []),
            "search_params": params,
            "success": True
        }

    def discover_brands(
        self,
        industry_keywords: str,
        region: str = "BR",
        min_ads: int = 5,
        limit: int = 20
    ) -> dict:
        """Descobre marcas por palavras-chave do setor"""
        keywords = [k.strip() for k in industry_keywords.split(",")]
        all_brands = {}

        for keyword in keywords:
            params = {
                'search_terms': keyword,
                'ad_reached_countries': [region],
                'fields': 'page_name,page_id',
                'limit': 100,
                'ad_active_status': 'ACTIVE'
            }

            result = self._make_request(params)

            if result.get("success") is False:
                continue

            for ad in result.get("data", []):
                page_name = ad.get("page_name", "")
                page_id = ad.get("page_id", "")
                if page_name and page_id:
                    key = f"{page_name}_{page_id}"
                    if key not in all_brands:
                        all_brands[key] = {
                            "page_name": page_name,
                            "page_id": page_id,
                            "keywords_matched": [],
                            "ad_count": 0
                        }
                    all_brands[key]["keywords_matched"].append(keyword)
                    all_brands[key]["ad_count"] += 1

        # Filtrar por min_ads e ordenar
        filtered = [
            v for v in all_brands.values()
            if v["ad_count"] >= min_ads
        ]
        filtered.sort(key=lambda x: x["ad_count"], reverse=True)

        return {
            "industry_keywords": industry_keywords,
            "region": region,
            "total_brands_found": len(filtered),
            "brands": filtered[:limit],
            "success": True
        }

    def analyze_creative(self, snapshot_url: str) -> dict:
        """Analisa criativo via Crawl4AI"""
        async def _crawl():
            async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
                result = await crawler.arun(snapshot_url)
                return {
                    "url": snapshot_url,
                    "success": result.success,
                    "markdown": result.markdown if hasattr(result, 'markdown') else None,
                    "cleaned_html": result.cleaned_html if result.cleaned_html else None,
                    "extracted_content": result.extracted_content if hasattr(result, 'extracted_content') else None,
                    "error": result.error_message if not result.success else None
                }

        try:
            return asyncio.run(_crawl())
        except Exception as e:
            return {"url": snapshot_url, "success": False, "error": str(e)}

    def get_ad_metrics(self, brand_name: str, country: str = "BR", days: int = 90) -> dict:
        """Pega métricas de performance de uma marca"""
        result = self.search_ads(brand_name, country, date_range=days, limit=100)

        if not result.get("success"):
            return result

        ads = result.get("ads", [])
        if not ads:
            return {"brand": brand_name, "success": True, "message": "Nenhum anúncio encontrado"}

        # Calcular métricas agregadas
        total_ads = len(ads)
        total_impressions = sum(
            sum(imp.get("upper_bound", 0) for imp in ad.get("impressions", {}).values())
            if isinstance(ad.get("impressions"), dict) else 0
            for ad in ads
        )
        total_spend = sum(
            sum(s.get("upper_bound", 0) for s in ad.get("spend", {}).values())
            if isinstance(ad.get("spend"), dict) else 0
            for ad in ads
        )

        platforms = {}
        for ad in ads:
            for p in ad.get("publisher_platforms", []):
                platforms[p] = platforms.get(p, 0) + 1

        # Anúncios mais recentes
        ads_sorted = sorted(ads, key=lambda x: x.get("ad_creation_time", ""), reverse=True)

        return {
            "brand": brand_name,
            "period_days": days,
            "total_ads": total_ads,
            "estimated_total_impressions": total_impressions,
            "estimated_total_spend": total_spend,
            "platforms_distribution": platforms,
            "latest_ads": ads_sorted[:10],
            "success": True
        }

    def compare_brands(self, brands: List[str], country: str = "BR", days: int = 30) -> dict:
        """Compara múltiplas marcas"""
        results = {}
        for brand in brands:
            results[brand] = self.get_ad_metrics(brand, country, days)

        return {
            "brands": brands,
            "comparison": results,
            "period_days": days,
            "country": country,
            "success": True
        }

    def export_to_csv(self, data: dict, filename: str) -> str:
        """Exporta dados para CSV"""
        import csv

        if "ads" not in data:
            return "Erro: dados não contêm lista de anúncios"

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ad_id', 'page_name', 'creation_time', 'creative_bodies',
                'link_titles', 'link_captions', 'link_descriptions',
                'snapshot_url', 'currency', 'impressions', 'spend',
                'platforms', 'regions'
            ])

            for ad in data["ads"]:
                impressions = ad.get("impressions", {})
                spend = ad.get("spend", {})

                writer.writerow([
                    ad.get("id", ""),
                    ad.get("page_name", ""),
                    ad.get("ad_creation_time", ""),
                    " | ".join(ad.get("ad_creative_bodies", [])),
                    " | ".join(ad.get("ad_creative_link_titles", [])),
                    " | ".join(ad.get("ad_creative_link_captions", [])),
                    " | ".join(ad.get("ad_creative_link_descriptions", [])),
                    ad.get("ad_snapshot_url", ""),
                    ad.get("currency", ""),
                    str(impressions),
                    str(spend),
                    ", ".join(ad.get("publisher_platforms", [])),
                    ", ".join(ad.get("delivery_by_region", []))
                ])

        return f"Exportado para {filename}"

    def generate_report(self, niche: str, brands: List[str], country: str = "BR") -> dict:
        """Gera relatório de inteligência"""
        comparison = self.compare_brands(brands, country, 90)

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

        for brand, data in comparison.get("comparison", {}).items():
            if data.get("success"):
                report["brand_details"][brand] = {
                    "total_ads": data.get("total_ads", 0),
                    "estimated_spend": data.get("estimated_total_spend", 0),
                    "platforms": data.get("platforms_distribution", {}),
                    "latest_ads_count": len(data.get("latest_ads", []))
                }

        # Insights básicos
        total_ads_all = sum(b.get("total_ads", 0) for b in report["brand_details"].values())
        total_spend_all = sum(b.get("estimated_spend", 0) for b in report["brand_details"].values())

        report["summary"] = {
            "total_ads_analyzed": total_ads_all,
            "estimated_total_market_spend": total_spend_all,
            "avg_ads_per_brand": total_ads_all / len(brands) if brands else 0
        }

        report["top_insights"] = [
            f"Mercado com {total_ads_all} anúncios ativos entre {len(brands)} marcas",
            f"Gasto estimado total: {total_spend_all:.0f} {country == 'BR' and 'BRL' or 'USD'}",
            "Top plataformas: " + ", ".join(set().union(*[set(b.get("platforms", {}).keys()) for b in report["brand_details"].values()]))
        ]

        report["recommendations"] = [
            "Teste criativos no formato Reels (maior alcance orgânico no BR)",
            "Use CTA direto para WhatsApp/PIX (conversão maior no Brasil)",
            "Segmente por interesse + lookalike 1% dos compradores",
            "Horários de pico BR: 12h-14h e 19h-22h",
            "Comece com CBO R$ 50-100/dia por ad set"
        ]

        return report


def main():
    parser = argparse.ArgumentParser(description="Facebook Ads Library - Direct CLI")
    parser.add_argument("--token", required=True, help="Facebook Access Token com ads_read")
    parser.add_argument("--brand", help="Nome da marca para buscar anúncios")
    parser.add_argument("--country", default="BR", help="Código do país (padrão: BR)")
    parser.add_argument("--days", type=int, default=30, help="Dias para buscar (padrão: 30)")
    parser.add_argument("--limit", type=int, default=50, help="Limite de anúncios (padrão: 50)")
    parser.add_argument("--discover", help="Palavras-chave para descobrir marcas (ex: 'curso online,ebook')")
    parser.add_argument("--min-ads", type=int, default=5, help="Mínimo de anúncios para discover")
    parser.add_argument("--analyze-url", help="URL do snapshot para analisar criativo")
    parser.add_argument("--compare", help="Marcas para comparar (separadas por vírgula)")
    parser.add_argument("--export", help="Arquivo CSV para exportar resultados")
    parser.add_argument("--report", help="Nicho para gerar relatório (use com --compare)")

    args = parser.parse_args()

    api = FacebookAdsDirect(args.token)

    if args.discover:
        print(f"\n🔍 Descobrindo marcas para: {args.discover} no {args.country}")
        result = api.discover_brands(args.discover, args.country, args.min_ads)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.analyze_url:
        print(f"\n🎨 Analisando criativo: {args.analyze_url}")
        result = api.analyze_creative(args.analyze_url)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.compare:
        brands = [b.strip() for b in args.compare.split(",")]
        print(f"\n📊 Comparando {len(brands)} marcas: {brands}")
        result = api.compare_brands(brands, args.country, args.days)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.brand:
        print(f"\n🔎 Buscando anúncios de: {args.brand} no {args.country} (últimos {args.days} dias)")
        result = api.search_ads(args.brand, args.country, date_range=args.days, limit=args.limit)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if args.export and result.get("success"):
            print(f"\n📤 Exportando para CSV...")
            msg = api.export_to_csv(result, args.export)
            print(msg)

    elif args.report and args.compare:
        brands = [b.strip() for b in args.compare.split(",")]
        print(f"\n📋 Gerando relatório para nicho: {args.report}")
        result = api.generate_report(args.report, brands, args.country)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()