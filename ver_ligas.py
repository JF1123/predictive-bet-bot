import requests

API_KEY = '059df6f2341b819b810c4fcab8de323e' 
url = f'https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}'

respuesta = requests.get(url)
deportes = respuesta.json()

print("⚽ Ligas de fútbol disponibles ahora mismo:")
for deporte in deportes:
    if 'soccer' in deporte['key']:
        print(f"- {deporte['title']} (Código: {deporte['key']})")