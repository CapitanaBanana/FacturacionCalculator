import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import os

def run(worksheet_name):
    base_dir = os.path.dirname(__file__)
    
    # Paso 1: Autenticarse con la API de Google
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(base_dir, "credencial.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    # Abrir la hoja de cálculo
    spreadsheet = client.open("Facturacion anual")
    worksheet = spreadsheet.worksheet(worksheet_name)

    # Paso 2: Leer el archivo txt
    with open(os.path.join(base_dir, 'resultado.txt'), 'r') as file:
        data = file.read()

    # Paso 3: Extraer la información relevante con expresiones regulares
    patron_cuit = re.compile(r"Cuit\s*(\d{11})")
    patron_vta = re.compile(r"^\d+:\s*([\d,]+)", re.MULTILINE)

    cuit_vta_dict = {}
    lines = data.strip().splitlines()
    current_cuit = None

    for line in lines:
        cuit_match = patron_cuit.search(line)
        vta_match = patron_vta.search(line)
        
        if cuit_match:
            current_cuit = cuit_match.group(1)
            if current_cuit not in cuit_vta_dict:
                cuit_vta_dict[current_cuit] = []
        elif vta_match and current_cuit:
            value = vta_match.group(1)
            cuit_vta_dict[current_cuit].append(value)

    # Paso 4: Escribir los datos en la hoja de cálculo
    messages = []
    all_values = worksheet.get_all_values()

    for cuit, vtas in cuit_vta_dict.items():
        found = False
        for row_num, row in enumerate(all_values):
            if cuit in row:
                found = True
                col_num = row.index(cuit)

                # Obtener el valor actual en la celda
                current_value = worksheet.cell(row_num + 1, col_num + 2).value

                # Crear una cadena con todos los valores separados por coma
                new_values = ', '.join(vtas)
                if len(vtas) > 1:
                    new_values = f"(la cuit tiene más de un punto de venta) {new_values}"

                # Solo actualizar si no están ya presentes
                if not current_value:
                    worksheet.update_cell(row_num + 1, col_num + 2, new_values)
                    messages.append(f"Actualizado CUIT {cuit} con valores de venta: {new_values}")
                # else:
                    # print(f"CUIT {cuit} ya tiene valores. No se actualizó.")
        
        if not found:
            messages.append(f"CUIT {cuit} no encontrado en la hoja.")

    # Devolver los mensajes acumulados
    return "\n".join(messages)
