import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import os
import tkinter as tk

def run():
  base_dir = os.path.join(os.path.dirname(__file__))

  # Paso 1: Autenticarse con la API de Google
  scope = ["https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"]
  creds_path = os.path.join(base_dir, "credencial.json")
  creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
  client = gspread.authorize(creds)

  # Abrir la hoja de cálculo
  spreadsheet = client.open(
      "Claves y anio 2024")  # Ajusta el nombre
  # Ajusta el nombre de la pestaña
  worksheet = spreadsheet.worksheet("Claves 2024 clientes mensuales")
  try:
    data = worksheet.get_all_values()

    # Filtrar filas donde ni la columna 4 ni la columna 7 estén vacías
    filas_filtradas = [fila for fila in data if len(fila) > 6 and fila[3] and fila[6]]

    # Extraer los valores de la columna 4 y la columna 7 solo de las filas filtradas
    columna_4 = [fila[3] for fila in filas_filtradas]  # Columna 4 (índice 3)
    columna_7 = [fila[6] for fila in filas_filtradas]  # Columna 7 (índice 6)

    # Crear archivo .txt para guardar los resultados
    output_file = os.path.join(base_dir, "Credentials.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
      # Iterar sobre las filas filtradas y escribir en el archivo
      for i, fila in enumerate(filas_filtradas):
          # Agregar un salto de línea solo si no es la última fila
          if i < len(filas_filtradas) - 1:
              f.write(f"[{fila[3]}] [{fila[6]}]\n")
          else:
              f.write(f"[{fila[3]}] [{fila[6]}]")
  except Exception as e:
    return f"Error al obtener las credenciales: {e}"
