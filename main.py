from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

# Configuración de NLTK
nltk.data.path.append('C:/Users/joell/AppData/Local/Programs/Python/Python312/Scripts/nltk_data')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Cargar los datos desde el CSV
def load_energy_data():
    df = pd.read_csv("Dataset/World_Energy_Consumption.csv")
    df = df.astype(str).fillna("")  # Rellenar valores vacíos con cadena vacía
    return df.to_dict(orient="records")

# Cargar datos al iniciar la API
energy_data = load_energy_data()

# Obtener sinónimos de palabras clave
def get_synonyms(word):
    synonyms = {word.lower()}  # Incluir la palabra original
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())
    return synonyms

# Inicializar FastAPI
app = FastAPI(title="Energy API", version="1.0.0")

@app.get("/", tags=["Home"])
def home():
    return HTMLResponse("<h1>Bienvenido a la API de Consumo de Energía</h1>")

@app.get("/energy", tags=["Energy"])
def get_energy_data():
    return energy_data or HTTPException(status_code=500, detail="No hay datos disponibles")

@app.get("/energy/{country}", tags=["Energy"])
def get_energy_by_country(country: str, year: int = None):
    results = [e for e in energy_data if e["country"].lower() == country.lower()]
    if year:
        results = [e for e in results if e["year"].isdigit() and int(e["year"]) == year]
    return results or {"detalle": "No se encontraron datos"}

@app.get("/chatbot", tags=["Chatbot"])
def chatbot(query: str):
    query_words = word_tokenize(query.lower())
    synonyms = set()

    # Generar sinónimos de las palabras clave
    for word in query_words:
        synonyms.update(get_synonyms(word))

    # Extraer datos clave de la consulta
    country = None
    year = None
    energy_type = None

    for word in query_words:
        if word.isdigit():  # Si es un número, asumimos que es un año
            year = int(word)
        elif word.title() in {e["country"] for e in energy_data}:  # Si está en la lista de países
            country = word.title()
        elif any(word in str(e.keys()).lower() for e in energy_data):  # Si es un tipo de energía
            energy_type = word

    # Generar respuestas según la consulta detectada
    if country and year:
        results = [e for e in energy_data if e["country"].lower() == country.lower() and int(e["year"]) == year]
        return results or {"respuesta": f"No encontré datos para {country} en {year}."}

    if country:
        results = [e for e in energy_data if e["country"].lower() == country.lower()]
        return results[:5] or {"respuesta": f"No encontré datos para {country}."}  # Máximo 5 resultados

    if energy_type and year:
        results = [e for e in energy_data if energy_type in e and int(e["year"]) == year]
        return results or {"respuesta": f"No encontré datos sobre {energy_type} en {year}."}

    if energy_type:
        results = [e for e in energy_data if energy_type in e]
        return results[:5] or {"respuesta": f"No encontré datos sobre {energy_type}."}  # Máximo 5 resultados

    return {"respuesta": "No entendí tu pregunta. Puedes intentar con algo como: 'Consumo de energía en España en 2020'."}


@app.get("/energy/by_type", tags=["Energy"])
def get_energy_by_type(energy_type: str):
    results = [e for e in energy_data if energy_type.lower() in str(e.values()).lower()]
    return results or {"detalle": "No se encontraron datos para este tipo de energía"}
