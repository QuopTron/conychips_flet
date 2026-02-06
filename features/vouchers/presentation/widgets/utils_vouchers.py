def format_bs(monto_cents: int) -> str:
    try:
        m = int(monto_cents)
    except Exception:
        try:
            m = int(round(float(monto_cents)))
        except Exception:
            m = 0
    return f"Bs {m/100:.2f}"

def breakdown_denominations(monto_cents: int) -> list:
    try:
        restante = int(monto_cents)
    except Exception:
        try:
            restante = int(round(float(monto_cents)))
        except Exception:
            restante = 0

    denoms = [20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50]
    labels = ["200 Bs", "100 Bs", "50 Bs", "20 Bs", "10 Bs", "5 Bs", "2 Bs", "1 Bs", "50 ctvs"]
    result = []
    for d, label in zip(denoms, labels):
        if restante <= 0:
            result.append((label, 0))
            continue
        cnt = restante // d
        result.append((label, int(cnt)))
        restante = restante - cnt * d

    return result
