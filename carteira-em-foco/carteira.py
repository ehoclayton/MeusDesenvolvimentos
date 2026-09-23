"""Compara duas fotografias CSV de uma carteira."""
import argparse
import csv
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED = {'id', 'cliente', 'valor', 'vencimento', 'status'}
STATUSES = {'a_faturar', 'emitido', 'pago'}


def load(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError(f'{path}: faltam colunas obrigatórias: {sorted(REQUIRED)}')
        items = {}
        for line, row in enumerate(reader, 2):
            try:
                item = {key: row[key].strip() for key in REQUIRED}
                item['valor'] = Decimal(item['valor'])
                item['vencimento'] = date.fromisoformat(item['vencimento'])
                if not item['id'] or not item['cliente'] or item['valor'] < 0 or not item['valor'].is_finite() or item['status'] not in STATUSES:
                    raise ValueError('campo inválido')
                if item['id'] in items:
                    raise ValueError('ID duplicado')
                items[item['id']] = item
            except (KeyError, TypeError, InvalidOperation, ValueError) as error:
                raise ValueError(f'{path}, linha {line}: {error}') from error
        return items


def month_end(day):
    return date(day.year + (day.month == 12), day.month % 12 + 1, 1) - timedelta(days=1)


def compare(before, after, reference):
    events = []
    for identifier in sorted(before.keys() | after.keys()):
        old, new = before.get(identifier), after.get(identifier)
        item = new or old
        def add(kind, left='', right='', value=None):
            events.append({'id': identifier, 'cliente': item['cliente'], 'evento': kind,
                           'valor': str(item['valor'] if value is None else value), 'antes': str(left), 'depois': str(right)})
        if old is None or new is None:
            add('incluido' if old is None else 'removido', old['vencimento'] if old else '', new['vencimento'] if new else '')
            continue
        if old['vencimento'] != new['vencimento']:
            a, b = old['vencimento'], new['vencimento']
            kind = 'adiado' if b > a else 'antecipado'
            if (a.year, a.month) == (reference.year, reference.month) and (b.year, b.month) > (reference.year, reference.month):
                kind = 'saiu_do_mes'
            elif b == month_end(reference):
                kind = 'foi_para_fim_do_mes'
            add(kind, a, b)
        if old['status'] != new['status']:
            add('status_alterado', old['status'], new['status'])
        if old['valor'] != new['valor']:
            add('valor_alterado', old['valor'], new['valor'], new['valor'] - old['valor'])
    return events


def report(events, reference):
    lines = [f'# Comparativo da carteira — {reference}', '', f'**{len(events)} alterações encontradas.**', '']
    for kind in ('saiu_do_mes', 'foi_para_fim_do_mes'):
        selected = [e for e in events if e['evento'] == kind]
        total = sum((Decimal(e['valor']) for e in selected), Decimal(0))
        money = f'{total:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        lines.append(f'- **{kind.replace("_", " ")}:** {len(selected)} item(ns), R$ {money}')
    lines += ['', '| ID | Cliente | Evento | Valor/variação (R$) | Antes | Depois |', '| --- | --- | --- | ---: | --- | --- |']
    for e in events:
        lines.append('| ' + ' | '.join(str(e[k]).replace('|', '\\|').replace('\n', ' ') for k in ('id', 'cliente', 'evento', 'valor', 'antes', 'depois')) + ' |')
    lines += ['', '_Volumes de prioridade somam valores atuais dos itens afetados; não indicam receita adicional ou perda realizada._', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('antes', type=Path)
    parser.add_argument('depois', type=Path)
    parser.add_argument('--referencia', required=True, type=date.fromisoformat)
    parser.add_argument('--saida', type=Path, default=Path('relatorio.md'))
    args = parser.parse_args()
    events = compare(load(args.antes), load(args.depois), args.referencia)
    args.saida.write_text(report(events, args.referencia), encoding='utf-8')
    print(f'{len(events)} alterações; relatório: {args.saida}')


if __name__ == '__main__':
    main()
