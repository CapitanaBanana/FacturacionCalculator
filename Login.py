from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


def login(credencial, path_to_chromedriver, download_path):
    user, password_txt = credencial
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    # Crea el servicio de ChromeDriver y el WebDriver dentro del proceso
    service = Service(executable_path=path_to_chromedriver)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 5)

    try:
        # print(f"Autenticando usuario: {user}")

        # Abrir la página de login
        driver.get("https://auth.afip.gob.ar/contribuyente_/login.xhtml")

        # Ingresar usuario
        cuil = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="F1:username"]')))
        cuil.clear()
        cuil.send_keys(user)

        # Hacer click en siguiente
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="F1:btnSiguiente"]'))).click()

        # Ingresar contraseña
        password = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="F1:password"]')))
        password.clear()
        password.send_keys(password_txt)

        # Ingresar
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="F1:btnIngresar"]'))).click()

        # Verificar si muestra cartel de cambiar contraseña
        try:
          wait.until(EC.presence_of_element_located((By.NAME, "F1:j_idt41")))
          return(f"Usuario {user} debe cambiar la contraseña.")
        except: 
          # Buscar la sección "Mis Comprobantes"
          misComprobantes = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="buscadorInput"]')))
          misComprobantes.clear()
          misComprobantes.send_keys("Mis Comprobantes")

          # Hacer click en el item "Mis Comprobantes"
          wait.until(EC.presence_of_element_located((By.XPATH, "//li[@aria-label='Mis Comprobantes']"))).click()
        # Comprobar si aparece el cartel emergente
        try:
            cartel = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='modal-content' and @role='document']")))
            if cartel:
              return(f"{user} cuenta no cuenta con la sección Mis Comprobantes.")
        except:
            # Cambiar a la nueva pestaña
            wait.until(lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[-1])

            # Hacer click en "Emitidos"
            wait.until(EC.element_to_be_clickable((By.XPATH, "//h3[text()='Emitidos']/ancestor::a"))).click()

            # Seleccionar "Mes pasado"
            wait.until(EC.element_to_be_clickable((By.ID, "fechaEmision"))).click()
            wait.until(EC.presence_of_element_located((By.XPATH, "//li[@data-range-key='Año Pasado']"))).click()

            # Buscar los comprobantes
            wait.until(EC.element_to_be_clickable((By.ID, "buscarComprobantes"))).click()

            # Exportar como CSV
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Exportar como CSV']"))).click()

            # Tiempo de espera para la descarga del archivo
            time.sleep(3)

    except Exception as e:
        return(f"Error con el usuario {user}, verificar manualmente!")
    finally:
        driver.quit()



