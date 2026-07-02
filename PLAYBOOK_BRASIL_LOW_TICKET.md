# 🇧🇷 Playbook: Low-Ticket Escalável no Brasil com Facebook Ads Library MCP

---

## 🎯 **Objetivo**
Encontrar produtos low-ticket (R$ 27-197) que **já estão escalando no Brasil**, analisar criativos vencedores, montar estratégia, estrutura e lançar.

---

## 📋 **Pré-requisitos**
- ✅ MCP configurado no Claude Desktop
- ✅ Token Facebook com permissão `ads_read`
- ✅ Conta de anúncios ativa (para validar depois)

---

## 🔍 **FASE 1: DESCOBERTA - Encontrar Produtos/Nichos Escalando**

### 1.1 Buscar por Palavras-chave de Nicho (Brasil)
```python
# No Claude Desktop:
"Use discover_competitor_brands com industry_keywords='curso online brasil', region='BR', min_ads=10, limit=50"
"Use discover_competitor_brands com industry_keywords='ebook brasil', region='BR', min_ads=10, limit=50"
"Use discover_competitor_brands com industry_keywords='mentoria brasil', region='BR', min_ads=5, limit=50"
"Use discover_competitor_brands com industry_keywords='planner digital brasil', region='BR', min_ads=5, limit=50"
"Use discover_competitor_brands com industry_keywords='receita fit brasil', region='BR', min_ads=5, limit=50"
```

### 1.2 Palavras-chave de Alta Conversão para Testar
| Nicho | Keywords para discover_competitor_brands |
|-------|------------------------------------------|
| **Info-produtos** | "curso online", "ebook", "mentoria", "masterclass", "workshop" |
| **Físicos low-ticket** | "kit", "combo", "box", "planner", "caderno", "organizador" |
| **Saúde/Beleza** | "suplemento", "creme", "serum", "vitamina", "detox" |
| **Casa/Organização** | "organizador", "kit cozinha", "cama mesa banho" |
| **Pet** | "ração", "brinquedo pet", "cama pet", "tapete higiênico" |

### 1.3 Filtrar Resultados - Critérios de "Já Escalando"
```python
# Após cada discover_competitor_brands, analise:
# ✅ Brands com 20+ anúncios ativos
# ✅ Brands aparecendo há 30+ dias (ad_creation_time antigo)
# ✅ Múltiplos criativos por brand (teste A/B ativo)
# ✅ Presença em Facebook + Instagram (publisher_platforms)
```

---

## 📊 **FASE 2: ANÁLISE PROFUNDA - Dissecar os Vencedores**

### 2.1 Buscar Anúncios Completos das Top Brands
```python
# Para cada brand promissora (top 5-10):
"Use search_facebook_ads com brand_name='NOME_DA_BRAND', country='BR', ad_type='ALL', date_range=90, limit=100"
```

### 2.2 Analisar Métricas de Performance
```python
# Para cada brand:
"Use analyze_ad_performance_metrics com brand_name='NOME_DA_BRAND', time_period=90"
```
**O que buscar:**
- `total_impressions` alto = escala
- `estimated_total_spend` alto = budget real
- `platform_distribution` = onde investem (IG Feed, Stories, Reels, FB Feed)
- `demographic_distribution` = público real (idade/gênero)

### 2.3 Análise de Criativos (O OURO)
```python
# Para CADA anúncio com snapshot_url dos top performers:
"Use analyze_ad_creative_elements com ad_snapshot_url='URL_DO_SNAPSHOT', extract_text=true, analyze_images=true, detect_cta=true"
```

**Extraia sistematicamente:**
| Elemento | O que Anotar |
|----------|--------------|
| **Hook** (primeiros 3s) | Frase de abertura, promessa, dor |
| **Corpo** | Benefícios, prova social, autoridade |
| **CTA** | Texto exato do botão, urgência |
| **Formato** | Vídeo? Carrossel? Imagem estática? Reels? |
| **Duração** (se vídeo) | <15s? 15-30s? 30-60s? |
| **Legendas** | Tem? Estilo? Emojis? |
| **Oferta** | Preço, bônus, garantia, escassez |

### 2.4 Análise Competitiva Multi-Brand
```python
# Compare as top 5-7 brands de uma vez:
"Use competitive_ad_analysis com brands_list=['BRAND1','BRAND2','BRAND3','BRAND4','BRAND5'], analysis_depth='deep'"
```
**Insights que isso te dá:**
- `market_leader` = quem domina volume
- `highest_spender` = quem tem budget
- `platform_trends` = onde o mercado está
- `common_themes` = palavras-chave que TODOS usam (validadas)

---

## 🧠 **FASE 3: ESTRATÉGIA - Montar o Plano de Ataque**

### 3.1 Relatório de Inteligência Completo
```python
# Para seu nicho escolhido + top concorrentes:
"Use generate_facebook_intelligence_report com brand_name='SUA_BRAND_OU_NICHO', include_competitors=true, report_depth='comprehensive'"
```

### 3.2 Template de Estratégia (Preencha com os Dados)

```
┌─────────────────────────────────────────────────────────────┐
│           ESTRATÉGIA LOW-TICKET BRASIL - [NICHO]            │
├─────────────────────────────────────────────────────────────┤
│ PRODUTO: [Nome] - Preço: R$ [XX] - Margem: [XX]%           │
│ AVATAR: [Idade] [Gênero] [Dor Principal] [Desejo]          │
├─────────────────────────────────────────────────────────────┤
│ CRIATIVOS VALIDADOS (do MCP):                               │
│   Hook 1: [Copiado do concorrente X - funcionou]           │
│   Hook 2: [Variação testada pelo concorrente Y]            │
│   Formato: [Vídeo 15s Reels + Carrossel 3 cards]           │
│   CTA: ["Quero meu acesso" / "Garantir minha vaga"]        │
├─────────────────────────────────────────────────────────────┤
│ ESTRUTURA DE CAMPANHA:                                      │
│   CBO: R$ [XX]/dia → 3 Ad Sets                             │
│     Ad Set 1: Lookalike 1% (compradores) - R$ [XX]         │
│     Ad Set 2: Interesse [nichos do demographic_distribution]│
│     Ad Set 3: Broad (sem segmentação) - R$ [XX]            │
│   3-5 anúncios por Ad Set (teste hook + formato)           │
├─────────────────────────────────────────────────────────────┤
│ MÉTRICAS-ALVO (benchmarks do MCP):                          │
│   CPL: R$ [XX] | CPA: R$ [XX] | ROAS: [X.X]                │
│   CTR: [X]% | Hook Rate: [X]% | Hold Rate: [X]%            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ **FASE 4: ESTRUTURA - Build da Máquina**

### 4.1 Assets Necessários (Baseado no MCP)
| Asset | Fonte | Status |
|-------|-------|--------|
| **Vídeos (3-5 hooks)** | Modelar top performers | ☐ Gravar |
| **Imagens carrossel** | Extrair themes do MCP | ☐ Design |
| **Copy longa (VSL/Artigo)** | Analisar ad_creative_bodies | ☐ Escrever |
| **Página de vendas** | Benchmark concorrentes | ☐ Build |
| **Pixel + CAPI** | Obrigatório | ☐ Configurar |
| **Domínio próprio** | Credibilidade | ☐ Comprar |

### 4.2 Estrutura Técnica no Gerenciador de Anúncios
```
Campanha: [NICHO] - Vendas - CBO
│
├── Ad Set 1: LAL 1% Compradores (30d)
│   ├── Anúncio 1: Hook A - Vídeo 15s
│   ├── Anúncio 2: Hook B - Vídeo 15s
│   ├── Anúncio 3: Carrossel Benefícios
│   └── Anúncio 4: Prova Social (prints)
│
├── Ad Set 2: Interesses (do demographic_distribution MCP)
│   ├── Anúncio 1: Hook A - Vídeo 15s
│   ├── Anúncio 2: Hook C - Reels nativo
│   └── Anúncio 3: Carrossel Objeções
│
└── Ad Set 3: Broad (sem segmentação)
    ├── Anúncio 1: Hook A - Vídeo 15s
    ├── Anúncio 2: UGC style
    └── Anúncio 3: Oferta Direta
```

### 4.3 Checklist Pré-Lançamento
- [ ] Pixel + Events API (CAPI) funcionando (teste com Event Manager)
- [ ] Domínio verificado no Business Manager
- [ ] Página de vendas carrega <3s (PageSpeed)
- [ ] Checkout testado (PIX + Cartão)
- [ ] UTM parameters em TUDO
- [ ] Relatórios automáticos configurados

---

## 🚀 **FASE 5: LANÇAMENTO E ESCALA**

### 5.1 Semana 1: Validação (R$ 50-100/dia)
```
OBJETIVO: Encontrar 1 combo Ad Set + Creative que dê ROAS > 1.5
AÇÕES:
  - Monitorar 3x/dia (manhã, tarde, noite)
  - Desligar anúncios com CTR < 1% ou CPL > 2x meta
  - Duplicar winners para novo Ad Set
```

### 5.2 Semana 2-3: Otimização (R$ 100-300/dia)
```
OBJETIVO: ROAS > 2.0 estável
AÇÕES:
  - Testar novos hooks (modelar MCP semanalmente)
  - Criar LAL 1% de compradores (quando 50+ sales)
  - Testar novos formatos (Reels, Stories, Collection)
  - Otimizar landing page (clarity, velocidade, copy)
```

### 5.3 Semana 4+: Escala (R$ 500+/dia)
```
OBJETIVO: Manter ROAS > 1.8 escalando budget
ESTRATÉGIAS:
  - Horizontal: Novos Ad Sets (interesses, LALs 2-3%, broad)
  - Vertical: Aumentar budget 20% a cada 2 dias nos winners
  - Creative refresh: 2 novos criativos/semana (use MCP p/ insp.)
  - Novos produtos: Cross-sell/upsell no thank you page
```

---

## 🔄 **ROTINA SEMANAL DE INTELIGÊNCIA (MCP)**

### Segunda - Monitoramento Concorrentes
```python
"Use search_facebook_ads com brand_name='CONCORRENTE_PRINCIPAL', country='BR', date_range=7, limit=50"
"Use analyze_ad_performance_metrics com brand_name='CONCORRENTE_PRINCIPAL', time_period=7"
```

### Quarta - Novos Entrantes
```python
"Use discover_competitor_brands com industry_keywords='SEU_NICHO', region='BR', min_ads=3, limit=20"
```

### Sexta - Creative Refresh
```python
# Buscar novos criativos dos tops
"Use search_facebook_ads com brand_name='TOP_COMPETITOR', country='BR', date_range=3, limit=20"
# Analisar criativos novos
"Use analyze_ad_creative_elements com ad_snapshot_url='NOVA_URL', extract_text=true, detect_cta=true"
```

---

## 📈 **KPIs PARA ACOMPANHAR DIARIAMENTE**

| Métrica | Meta Low-Ticket BR | Ação se Abaixo |
|---------|-------------------|----------------|
| **CTR** | > 1.5% | Trocar creative/hook |
| **CPL** | < R$ 15 | Melhorar segmentação/oferta |
| **CPA** | < 30% do preço | Otimizar LP, trocar oferta |
| **ROAS** | > 1.5 | Pausar, analisar, reiniciar |
| **Hook Rate (3s)** | > 25% | Primeiros 3s do vídeo |
| **Hold Rate (15s)** | > 15% | Roteiro/edicao do vídeo |

---

## 💡 **HACKS ESPECÍFICOS BRASIL (do MCP)**

### 1. **Horários de Ouro** (validate no delivery_by_region)
- 6h-9h: Café da manhã / deslocamento
- 12h-14h: Almoço
- 18h-22h: **PICO** - maior competição, maior volume

### 2. **Formatos que Convertem no BR** (publisher_platforms)
1. **Reels** (maior reach orgânico + pago)
2. **Stories** (menor CPC, bom para remarketing)
3. **Feed Instagram** (melhor conversão direta)
4. **Feed Facebook** (público 35+, ticket médio maior)

### 3. **Copy que Funciona no BR** (sentiment_keywords do MCP)
- "Brasileiro", "Aqui no Brasil", "Nacional"
- "PIX", "Boleto", "Parcelado sem juros"
- "Garantia 7 dias", "Risco zero"
- "Comunidade", "Grupo VIP", "Suporte WhatsApp"

---

## 🛠️ **COMANDOS RÁPIDOS PARA CLAUDE DESKTOP**

### Descoberta Inicial
```
"Descubra marcas de 'curso de inglês brasil' com min_ads=10 no Brasil"
"Descubra marcas de 'planner digital brasil' com min_ads=5 no Brasil"
```

### Análise Profunda
```
"Analise performance da marca 'NOME' nos últimos 90 dias no Brasil"
"Analise o criativo deste snapshot: [URL]"
"Compare as marcas: ['Marca1','Marca2','Marca3','Marca4','Marca5']"
```

### Relatório Completo
```
"Gere relatório de inteligência completo para 'NICHO' incluindo concorrentes no Brasil"
```

### Export para Trabalhar Offline
```
"Exporte todos os anúncios da 'MARCA' em CSV com criativos para eu analisar no Excel"
"Exporte em Markdown para eu colocar no Notion"
```

---

## ⚠️ **ERROS COMUNS PARA EVITAR**

| Erro | Consequência | Correção |
|------|--------------|----------|
| Copiar criativo 1:1 | Banimento, baixa conversão | **Modelar estrutura, criar original** |
| Não testar hooks | Budget queimado | Mínimo 3 hooks diferentes |
| Broad sem pixel maduro | CPL altíssimo | Pixel precisa de 50+ eventos |
| Ignorar Reels | Perde 40%+ reach | Sempre ter creative vertical 9:16 |
| Não monitorar concorrentes | Fica obsoleto | Rotina semanal obrigatória |
| Escalar cedo demais | ROAS cai | Regra: 3 dias ROAS estável antes de subir |

---

## 📅 **CRONOGRAMA DE 30 DIAS**

| Semana | Foco | Budget | Meta |
|--------|------|--------|------|
| 1 | Pesquisa MCP + Build assets | R$ 0 | 5 hooks, 3 créatifs, LP pronta |
| 2 | Lançamento + Validação | R$ 50/dia | 1 winner ROAS > 1.5 |
| 3 | Otimização + LAL | R$ 150/dia | ROAS > 2.0 estável |
| 4 | Escala Horizontal | R$ 500+/dia | ROAS > 1.8, volume alto |

---

## 🎓 **PRÓXIMOS NÍVEIS (Pós-Escala)**

1. **WhatsApp Funnel** - Capturar lead → Nutrir → Vender high-ticket
2. **Email Marketing** - Sequência 7 dias + broadcast semanais
3. **Afiliados** - Recrutar com comissão 30-50%
4. **Produtos Complementares** - Order bump, upsell, downsell
5. **Própria Rede de Afiliados** - Escala exponencial

---

## 🔗 **RECURSOS ÚTEIS**

- **Facebook Ads Library**: facebook.com/ads/library
- **Graph API Explorer**: developers.facebook.com/tools/explorer
- **Crawl4AI Docs**: github.com/unclecode/crawl4ai
- **FastMCP Docs**: github.com/modelcontextprotocol/python-sdk

---

*Playbook criado baseado no facebook-ads-library-mcp v1.0*
*Atualize semanalmente com novos insights do MCP*