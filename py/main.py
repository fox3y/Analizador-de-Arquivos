import os
import string
import sys
import time
import subprocess
import platform
from difflib import SequenceMatcher
from pathlib import Path


def listar_locais_de_busca():
    """Retorna uma lista de pastas comuns para procurar arquivos."""
    home = Path.home()
    locais = []

    if home.exists():
        locais.extend(
            [
                home,
                home / "Downloads",
                home / "Documents",
                home / "Desktop",
                home / "Pictures",
                home / "Videos",
                home / "Music",
            ]
        )

    for letra in string.ascii_uppercase:
        caminho = Path(f"{letra}:\\")
        try:
            if caminho.exists():
                locais.append(caminho)
        except OSError:
            continue

    return [str(caminho) for caminho in locais if caminho.exists()]


def localizar_arquivos_recentes(locais, dias=90):
    """Retorna arquivos recentes em uma lista de pastas, incluindo subpastas."""
    if isinstance(locais, (str, os.PathLike)):
        locais = [locais]

    limite = time.time() - (dias * 24 * 60 * 60)
    arquivos = []

    for pasta in locais:
        if not os.path.isdir(pasta):
            continue

        for raiz, _, arquivos_da_pasta in os.walk(pasta, onerror=lambda _erro: None):
            for nome in arquivos_da_pasta:
                caminho = os.path.join(raiz, nome)
                try:
                    if os.path.isfile(caminho):
                        data_mod = os.path.getmtime(caminho)
                        if data_mod >= limite:
                            arquivos.append((data_mod, caminho))
                except OSError:
                    continue

    arquivos.sort(key=lambda item: item[0], reverse=True)
    return [caminho for _, caminho in arquivos]


def encontrar_resultados(nome_busca, arquivos, limite=10):
    """Retorna os arquivos mais parecidos com o nome buscado."""
    if not arquivos:
        return []

    termo = nome_busca.casefold()
    resultados = []

    for caminho in arquivos:
        nome = Path(caminho).name
        nome_normalizado = nome.casefold()

        if termo in nome_normalizado or nome_normalizado in termo:
            score = 1.0
        else:
            score = SequenceMatcher(None, termo, nome_normalizado).ratio()

        if score >= 0.3:
            resultados.append((score, caminho))

    resultados.sort(key=lambda item: item[0], reverse=True)
    return resultados[:limite]


def executar_buscador():
    """Função principal do buscador interativo."""
    print("=== Buscador de arquivos ===")
    print("Digite 'sair' para encerrar.\n")

    while True:
        termo = input("Digite o nome do arquivo que deseja achar: ").strip()

        if termo.lower() in {"", "sair", "exit"}:
            print("Encerrando o programa...")
            break

        locais = listar_locais_de_busca()

        try:
            arquivos = localizar_arquivos_recentes(locais)
        except FileNotFoundError as erro:
            print(erro)
            continue

        if not arquivos:
            print("Nenhum arquivo recente encontrado nas pastas pesquisadas.")
            continue

        resultados = encontrar_resultados(termo, arquivos, limite=10)

        if not resultados:
            print("Nenhum arquivo parecido foi encontrado.")
            continue

        print("\nPossíveis resultados:")
        for indice, (score, caminho) in enumerate(resultados, start=1):
            print(f"{indice}. {Path(caminho).name} (similaridade: {score:.2f})")
            print(f"   {caminho}")

        print()


if __name__ == "__main__":
    # Se foi passado argumento --run, executa o buscador
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        executar_buscador()
    else:
        # Sempre tenta abrir um terminal separado
        script_path = os.path.abspath(__file__)
        sistema = platform.system()

        try:
            if sistema == "Windows":
                os.system(f'start cmd /k python "{script_path}" --run')
            elif sistema == "Darwin":
                os.system(f'open -a Terminal "{script_path}"')
            elif sistema == "Linux":
                os.system(f'gnome-terminal -- python "{script_path}" --run &')
        except Exception as e:
            print(f"Erro ao abrir terminal: {e}")
            executar_buscador()

