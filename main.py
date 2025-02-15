from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd

# Cargar los datos desde el archivo CSV
def load_energy_data():
    df = pd.read_csv("Dataset/World_Energy_Consumption.csv")
    df = df.fillna('').astype(str)  # Convierte todo a string después de reemplazar nulos
    return df

# Cargamos los datos al iniciar la API
data = load_energy_data()

# Inicializamos la API
app = FastAPI(title="API de Consumo de Energía", version="1.0.0")

# Ruta de bienvenida
@app.get("/")
def home():
    return JSONResponse(content={"mensaje": "Bienvenido a la API de Consumo de Energía"})

# Obtener todos los datos
@app.get("/energy")
def get_all_energy_data():
    return data.to_dict(orient='records')

# Buscar por país y/o año
@app.get("/energy/search")
def search_energy_data(country: str = None, year: int = None):
    df_filtered = data.copy()
    if country:
        df_filtered = df_filtered[df_filtered['country'].str.lower() == country.lower()]
    if year:
        df_filtered = df_filtered[df_filtered['year'] == year]
    
    if df_filtered.empty:
        raise HTTPException(status_code=404, detail="No se encontraron resultados")
    
    return df_filtered.to_dict(orient='records')

# Filtrar por tipo de energía
@app.get("/energy/type")
def filter_by_energy_type(energy_type: str):
    energy_columns = [col for col in data.columns if energy_type.lower() in col.lower()]
    
    if not energy_columns:
        raise HTTPException(status_code=400, detail="Tipo de energía no válido")
    
    df_filtered = data[['country', 'year'] + energy_columns]
    return df_filtered.to_dict(orient='records')
