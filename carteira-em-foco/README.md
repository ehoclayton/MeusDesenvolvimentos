# Carteira em Foco

Comparador de snapshots CSV para acompanhar mudanças em uma carteira de faturamento. Transforma duas fotografias da carteira em um relatório e destaca vencimentos que saíram do mês de referência ou foram deslocados para seu último dia.

> Projeto demonstrativo. Empresas e valores são fictícios; não há dados profissionais reais.

## Por que existe

O saldo atual não mostra o que mudou desde a última conferência. O programa compara itens pelo ID, separa alterações de vencimento, status e valor e mostra prioridades para acompanhamento. Uma mesma AF pode gerar mais de um evento.

## Executar

Requer Python 3.10 ou superior; usa somente a biblioteca padrão.

```bash
python carteira.py examples/antes.csv examples/depois.csv --referencia 2026-09-23 --saida relatorio.md
```

Abra `relatorio.md` para consultar o resumo e os eventos. Verificações:

```bash
python -m unittest discover -s tests -v
```

## Dados e regras

Cada CSV contém `id,cliente,valor,vencimento,status`. O ID é único por arquivo; o valor usa ponto decimal; a data usa `AAAA-MM-DD`; o status aceita `a_faturar`, `emitido` ou `pago`. Registros inválidos são rejeitados com arquivo e linha.

| Condição | Evento |
| --- | --- |
| Vencimento do mês de referência foi para mês posterior | `saiu_do_mes` |
| Vencimento mudou para o último dia do mês de referência | `foi_para_fim_do_mes` |
| Outra mudança de vencimento | `adiado` ou `antecipado` |
| Status ou valor mudou | Evento independente |
| ID apareceu ou desapareceu | `incluido` ou `removido` |

O volume das prioridades soma o **valor atual dos itens afetados**. Não significa receita adicional nem perda realizada. O programa não presume causas nem atribui responsabilidades.

## Evolução possível

Importação de Excel, histórico das comparações e painel por período e empresa. Este exemplo mantém as regras simples e auditáveis para demonstrar o raciocínio.
