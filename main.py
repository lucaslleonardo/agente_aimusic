import os
import requests
from dotenv import load_dotenv

load_dotenv()
chave = os.getenv("LASTFM_API_KEY")
URL = "http://ws.audioscrobbler.com/2.0/"

# --------------------

def pedir_artista(numero):
    while True:
        nome = input(f"Digite o {numero}º artista: ").strip()
        if nome:
            return nome
        print("ERRO! Resposta em branco.")


def listar_artistas(lista):
    print(" ")
    print("Artistas selecionados:")

    for indice, artista in enumerate(lista, start=1):
        print(f"{indice}. {artista}")


def sugerir_artista(nome):
    # add api
    sobre = buscar_sobre(nome)
    print(" ")
    print(f"Artista sugerido: {nome}\nSobre: {sobre}")
    print(" ")


def sugerir_album(nome):
    albuns = buscar_albuns(nome)

    if not albuns:
        print("Nenhum álbum encontrado.")
        return

    for i, album in enumerate(albuns):
        print(" ")
        print(f"Álbum sugerido: {album}")
        print(" ")

        if confirmar("Deseja ouvir este álbum? (sim/não): "):
            print("Boa escuta!")
            return

        if i < len(albuns) - 1:
            if not confirmar("Deseja sugestão de outro álbum? (sim/não): "):
                return

    print("Esses foram todos os álbuns que encontrei.")


def confirmar(pergunta):
    while True:
        resposta = input(pergunta).strip().lower()
        if resposta in ["sim", "s"]:
            return True
        if resposta in ["não", "nao", "n"]:
            return False
        print("Digite sim ou não.")


def contar_tags_em_comum(artistas_usuario, candidato):
    tags_candidato = buscar_tags(candidato)
    pontos = 0

    for artista in artistas_usuario:
        for tag in buscar_tags(artista):
            if tag in tags_candidato:
                pontos += 1

    return pontos

def escolher_candidato(artistas_usuario, candidatos):
    melhor_candidato = None
    melhor_pontuacao = -1

    for candidato in candidatos:
        pontos = contar_tags_em_comum(artistas_usuario, candidato)
        if pontos > melhor_pontuacao:
            melhor_candidato = candidato
            melhor_pontuacao = pontos

    return melhor_candidato

def buscar_tags(artista):
    parametros = {
        "method": "artist.getTopTags",
        "artist": artista,
        "api_key": chave,
        "format": "json",
    }

    resposta = requests.get(URL, params=parametros)
    dados = resposta.json()

    nomes = []
    for tag in dados["toptags"]["tag"][:4]:
        nomes.append(tag["name"].lower())

    return nomes


def buscar_similares(artista):
    parametros = {
        "method": "artist.getSimilar",
        "artist": artista,
        "api_key": chave,
        "format": "json",
        "limit": 5,
    }

    resposta = requests.get(URL, params=parametros)
    dados = resposta.json()

    nomes = []
    for item in dados["similarartists"]["artist"]:
        nomes.append(item["name"])

    return nomes

def buscar_albuns(artista):
    parametros = {
        "method": "artist.getTopAlbums",
        "artist": artista,
        "api_key": chave,
        "format": "json",
        "limit": 5,
    }

    resposta = requests.get(URL, params= parametros)
    dados = resposta.json()

    nomes=[]
    for album in dados["topalbums"]["album"]:
        if album["name"] != "(null)":
            nomes.append(album["name"])

    return nomes


def buscar_sobre(artista):
    parametros = {
        "method": "artist.getInfo",
        "artist": artista,
        "api_key": chave,
        "format": "json",
    }

    resposta = requests.get(URL, params=parametros)
    dados = resposta.json()

    resumo = dados["artist"]["bio"]["summary"]
    resumo = resumo.split("<a href")[0].strip()

    if not resumo:
        return "Sem informações disponíveis."
    return resumo

# --------------------


artistas = []

for i in range(1, 4):
    nome = pedir_artista(i)
    artistas.append(nome)

listar_artistas(artistas)

# candidatos = sugestões que o usuário NÃO digitou
candidatos = []
for artista in artistas:
    for similar in buscar_similares(artista):
        if similar not in artistas and similar not in candidatos:
            candidatos.append(similar)

aceitou = False

while candidatos:
    artista_da_vez = escolher_candidato(artistas, candidatos)
    sugerir_artista(artista_da_vez)

    if confirmar(f"Deseja ouvir {artista_da_vez}? (sim/não): "):
        aceitou = True
        print("Gerando sugestão...")
        sugerir_album(artista_da_vez)
        break

    candidatos.remove(artista_da_vez)

    if candidatos:
        if not confirmar("Deseja sugestão de outro artista? (sim/não): "):
            break

if not aceitou:
    print("Ok! Até a próxima!")