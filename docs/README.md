# Documentos para IAs (prompts)

Nomenclatura: **`roteiro-{destino}-{ano}-{tipo}.{ext}`**

| Ficheiro | Tipo | Para quê |
|----------|------|----------|
| `roteiro-europa-2026-prompt-mestre` | **mestre** | Plano completo (dias, voos, hotéis, legs) — anexar na IA ou no telemóvel |
| `roteiro-europa-2026-prompt-atualizacoes` | **atualizações** | Só o que mudou — usar **com** o mestre se a IA tiver contexto antigo |
| `arquivo/*` | **arquivo** | Notas antigas supersedidas (não regenerar PDF) |

## Regenerar PDF

```bash
# Plano completo (default)
python3 scripts/generate_prompt_pdf.py

# Só atualizações
python3 scripts/generate_prompt_pdf.py docs/roteiro-europa-2026-prompt-atualizacoes.txt

# Ambos
python3 scripts/generate_prompt_pdf.py --all
```

Gera `.pdf` + `.html` (intermédio) ao lado do `.txt`. Requer Google Chrome (macOS).

## Uso numa IA

| Situação | Anexar |
|----------|--------|
| IA nova / sem histórico | `roteiro-europa-2026-prompt-mestre.pdf` |
| IA ainda menciona Bruges ou dia 6 vazio | mestre + `roteiro-europa-2026-prompt-atualizacoes.pdf` |

Fonte canónica do site: `../index.html`.
