import json
import random
from urllib.request import Request, urlopen

API_URL = "http://18.216.124.191:8000"
QUANTIDADE_USUARIOS = 100

# Pontos-base aproximados dentro da região urbana de Vila Velha.
# São apenas coordenadas para geração de massa de teste.
PONTOS_BASE = [
    (-20.3290, -40.2920),
    (-20.3400, -40.2940),
    (-20.3500, -40.3000),
    (-20.3620, -40.3040),
    (-20.3750, -40.3100),
    (-20.3900, -40.3200),
    (-20.3420, -40.3250),
    (-20.3600, -40.3400)
]

def gerar_posicao():
    latitude_base, longitude_base = random.choice(PONTOS_BASE)

    # Espalha cada pessoa alguns quarteirões ao redor do ponto-base.
    latitude = latitude_base + random.uniform(-0.006, 0.006)
    longitude = longitude_base + random.uniform(-0.006, 0.006)

    return latitude, longitude

def inserir_pessoa(numero):
    latitude, longitude = gerar_posicao()

    dados = {
        "device_id": f"fake-{numero:03d}",
        "latitude": latitude,
        "longitude": longitude
    }

    body = json.dumps(dados).encode("utf-8")

    request = Request(
        f"{API_URL}/locations",
        data=body,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urlopen(request, timeout=10) as response:
        resultado = response.read().decode("utf-8")

    print(
        f"fake-{numero:03d} -> "
        f"{latitude:.6f}, {longitude:.6f}"
    )

    return resultado

def main():
    sucesso = 0
    erros = 0

    print(
        f"Inserindo {QUANTIDADE_USUARIOS} pessoas fictícias..."
    )

    for numero in range(1, QUANTIDADE_USUARIOS + 1):
        try:
            inserir_pessoa(numero)
            sucesso += 1
        except Exception as error:
            erros += 1
            print(
                f"Erro fake-{numero:03d}: {error}"
            )

    print()
    print("Finalizado")
    print(f"Sucesso: {sucesso}")
    print(f"Erros: {erros}")

if __name__ == "__main__":
    main()