"""
run_daily_screener.py
Script standalone para execução via GitHub Actions (ou local).
Importa a lógica do screener e salva os resultados em disco.
"""

import datetime
import sys
from screener_logic import run_screener


def main():
    print("=" * 60)
    print("  Week Screener SMC — Execução Diária Automática")
    print("=" * 60)
    print(f"Início: {datetime.datetime.utcnow().isoformat()}Z (UTC)")
    print()

    try:
        signals = run_screener('tickers_b3.csv')
    except Exception as e:
        print(f"ERRO FATAL ao executar screener: {e}")
        sys.exit(1)

    now = datetime.datetime.utcnow()

    if signals is not None and not signals.empty:
        # Salva o DataFrame completo
        signals.to_csv("latest_scan.csv", index=False)
        print(f"\n✅ {len(signals)} sinais salvos em latest_scan.csv")
    else:
        # Mesmo sem sinais, salva um CSV vazio com cabeçalhos para indicar que rodou
        import pandas as pd
        pd.DataFrame(columns=[
            'Ticker', 'Sinal', 'Tipo', 'Preço', 'POI', 'POI Preço',
            'Zona', 'SL', 'TP1', 'RR', 'Dist. POI', 'Nota MTF'
        ]).to_csv("latest_scan.csv", index=False)
        print("\n⚠️ Nenhum sinal ativo encontrado. CSV vazio salvo.")

    # Salva timestamp da execução
    with open("latest_run.txt", "w") as f:
        f.write(now.isoformat())
    print(f"🕐 Timestamp salvo em latest_run.txt: {now.isoformat()}")

    print()
    print("=" * 60)
    print("  Execução concluída com sucesso.")
    print("=" * 60)


if __name__ == '__main__':
    main()
