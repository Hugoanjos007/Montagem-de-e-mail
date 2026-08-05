import os
import time
import shutil

from selenium.webdriver.common import options
import schedule
from datetime import datetime
from PIL import Image
import win32clipboard
import win32com.client as win32

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIGURAÇÕES =================
USUARIO = "hugo.anjos"
SENHA = "Fort2022@"
TIMEOUT = 20

URL_LOGIN = "http://192.168.15.201/crm/login.php"
URL_RELATORIO_1 = "http://192.168.15.201/crm/index.php?codmodulo=389"
URL_RELATORIO_2 = "http://192.168.15.201/crm/index.php?codmodulo=446"
URL_RELATORIO_3 = "http://192.168.15.201/crm/index.php?codmodulo=516"

PASTA_RELATORIO_1 = r"\\192.168.15.102\e\CaeduADM\RELATÓRIOS\2025\04.Abril\powerquery\pesquisa hr a hr relatorio chamada"
PASTA_RELATORIO_2 = r"\\192.168.15.102\e\CaeduADM\RELATÓRIOS\2025\04.Abril\powerquery\ura satisfaçao pesquisa analitica"
PASTA_RELATORIO_3 = r"\\192.168.15.102\e\CaeduADM\RELATÓRIOS\2025\04.Abril\powerquery\SMS"

PASTA_TEMP_DOWNLOAD = r"C:\Temp\downloads_crm"
PASTA_PRINTS_LOCAL = r"\\192.168.15.102\e\CaeduADM\RELATÓRIOS\2026\Pesquisa hora a hora do dia"
PASTA_REDE_INDICADORES = r"X:\INDICADORES MANHA E TARDE"

CAMINHO_EXCEL = r"C:\pesq\Relatório hora a hora 5.xlsm"

NOME_MACRO_PRINCIPAL = "Planilha4.FiltrarTabelaDinamicaPorColunaA"
NOME_MACRO_DASHBOARD = "Dashboard_Seguro"

TEAMS_URL = "https://teams.live.com/v2/"
CHROME_PROFILE = r"C:\ChromeProfiles\Teams"

# ================= UTILITÁRIOS =================
def log(msg):
    print(f"[{datetime.now().strftime('%d/%m %H:%M:%S')}] {msg}")

def limpar_pasta(pasta):
    os.makedirs(pasta, exist_ok=True)
    for f in os.listdir(pasta):
        caminho = os.path.join(pasta, f)
        if os.path.isfile(caminho):
            try:
                os.remove(caminho)
            except:
                pass

def aguardar_download(pasta, extensoes=(".csv", ".xlsx", ".xls"), timeout=180):
    fim = time.time() + timeout
    while time.time() < fim:
        arquivos = [
            os.path.join(pasta, a)
            for a in os.listdir(pasta)
            if a.lower().endswith(extensoes)
        ]
        parciais = [a for a in os.listdir(pasta) if a.endswith(".crdownload")]
        if arquivos and not parciais:
            return max(arquivos, key=os.path.getmtime)
        time.sleep(1)
    raise TimeoutError("Download não concluído no tempo esperado.")

def mover_arquivo(origem, destino):
    os.makedirs(destino, exist_ok=True)
    shutil.move(origem, os.path.join(destino, os.path.basename(origem)))

def salvar_print(ws, intervalo, nome_arquivo):
    ws.Activate()
    rng = ws.Range(intervalo)
    rng.CopyPicture(Appearance=1, Format=2)
    time.sleep(4)

    chart = ws.ChartObjects().Add(0, 0, rng.Width, rng.Height)
    chart.Chart.Paste()
    chart.Chart.Export(nome_arquivo)
    chart.Delete()

    log(f"📸 Print salvo: {os.path.basename(nome_arquivo)}")

# ================= CLIPBOARD (TEAMS) =================
def copiar_imagem_clipboard(caminho):
    img = Image.open(caminho).convert("RGB")

    temp_bmp = os.path.join(os.environ["TEMP"], "clipboard_image.bmp")
    img.save(temp_bmp, "BMP")

    with open(temp_bmp, "rb") as f:
        data = f.read()[14:]

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def ultimas_duas_imagens(pasta):
    arquivos = [
        os.path.join(pasta, f)
        for f in os.listdir(pasta)
        if f.lower().endswith(".png")
    ]
    arquivos.sort(key=os.path.getmtime, reverse=True)
    return arquivos[:2]

# ================= ENVIO TEAMS =================
def enviar_teams():
    log("➡️ Abrindo Teams")

    options = Options()
    options.add_argument("--start-minimized")
    options.add_argument("--disable-notifications")
    options.add_argument(f"--user-data-dir={CHROME_PROFILE}")
    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 120)
    driver.get(TEAMS_URL)

    campo_msg = wait.until(EC.presence_of_element_located((
        By.XPATH, "//div[@contenteditable='true' and @role='textbox']"
    )))

    campo_msg.click()
    time.sleep(1)

    prints = ultimas_duas_imagens(PASTA_PRINTS_LOCAL)

    if len(prints) < 2:
        log("❌ Não foram encontradas 2 imagens para envio")
        driver.quit()
        return

    hora = datetime.now().strftime("%Hh%M")

    log("📤 Enviando imagens no chat")

    for img in reversed(prints):
        copiar_imagem_clipboard(img)
        time.sleep(1)
        campo_msg.send_keys(Keys.CONTROL, "v")
        time.sleep(3)

    campo_msg.send_keys(f" {hora}")
    time.sleep(1)
    campo_msg.send_keys(Keys.ENTER)

    log("✅ Mensagem enviada com sucesso")

    time.sleep(5)
    driver.quit()

# ================= AUTOMAÇÃO PRINCIPAL =================
def executar_automacao():

    hora_atual = datetime.now().hour
    if not (10 <= hora_atual <= 21):
        log("⏳ Fora do horário permitido")
        return

    log(f"🚀 Iniciando ciclo das {hora_atual}:00")

    limpar_pasta(PASTA_TEMP_DOWNLOAD)
    limpar_pasta(PASTA_RELATORIO_1)
    limpar_pasta(PASTA_RELATORIO_2)
    limpar_pasta(PASTA_RELATORIO_3)

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": PASTA_TEMP_DOWNLOAD,
        "download.prompt_for_download": False
    })

    # Código atualizado para o Python 3.13 / Selenium 4+
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, TIMEOUT)

    try:
        log("🔐 Login no CRM")
        driver.get(URL_LOGIN)

        wait.until(EC.presence_of_element_located((By.ID, "l_login"))).send_keys(USUARIO)
        driver.find_element(By.ID, "l_senha").send_keys(SENHA)
        driver.execute_script("enviarDados();")

        wait.until(EC.url_contains("index.php"))
        log("✅ Login realizado")

        log("📊 Relatório 1")
        driver.get(URL_RELATORIO_1)
        wait.until(EC.element_to_be_clickable((By.ID, "btn_pesquisar"))).click()
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'csv') or contains(@src,'excel')]/ancestor::span"))
        ).click()
        mover_arquivo(aguardar_download(PASTA_TEMP_DOWNLOAD), PASTA_RELATORIO_1)

        log("📊 Relatório 2")
        driver.get(URL_RELATORIO_2)
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'csv') or contains(@src,'excel')]/ancestor::span"))
        ).click()
        mover_arquivo(aguardar_download(PASTA_TEMP_DOWNLOAD), PASTA_RELATORIO_2)

        log("📊 Relatório 3")
        driver.get(URL_RELATORIO_3)
        wait.until(EC.presence_of_element_located((By.ID, "agrupador")))

        driver.execute_script("""
            var select = document.getElementById('agrupador');
            select.value = 'usuario';
            select.dispatchEvent(new Event('change'));
        """)
        time.sleep(1)

        wait.until(EC.element_to_be_clickable((By.ID, "btn_pesquisar"))).click()
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//img[contains(@src,'csv') or contains(@src,'excel')]/ancestor::span"))
        ).click()
        mover_arquivo(aguardar_download(PASTA_TEMP_DOWNLOAD), PASTA_RELATORIO_3)

    finally:
        driver.quit()

    # ================= EXCEL =================
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = True
    excel.DisplayAlerts = False

    wb = excel.Workbooks.Open(CAMINHO_EXCEL)

    for i in range(3):
        log(f"🔄 RefreshAll ({i+1}/3)")
        wb.RefreshAll()
        time.sleep(10)

    log("▶ Macro principal")
    excel.Run(f"'{wb.Name}'!{NOME_MACRO_PRINCIPAL}")
    time.sleep(5)

    wb.RefreshAll()
    time.sleep(10)

    log("▶ Macro Dashboard")
    excel.Run(f"'{wb.Name}'!{NOME_MACRO_DASHBOARD}")
    time.sleep(5)

    hora_str = datetime.now().strftime("%Hh%Mm")

    salvar_print(
        wb.Worksheets("Dashboard"),
        "A1:Q36",
        os.path.join(PASTA_PRINTS_LOCAL, f"{hora_str} Dashboard.png")
    )

    ws = wb.Worksheets("Analitico")
    valores = ws.Range("B1:B200").Value

    u_lin = 4
    for i, r in enumerate(valores):
        if r[0]:
            u_lin = i + 1

    intervalo = f"A1:U{u_lin}"

    salvar_print(
        ws,
        intervalo,
        os.path.join(PASTA_PRINTS_LOCAL, f"{hora_str} Analitico.png")
    )

    salvar_print(
        ws,
        intervalo,
        os.path.join(PASTA_REDE_INDICADORES, f"{hora_str} Analitico.png")
    )

    # >>>>>>> NOVO COMPORTAMENTO (SEU PEDIDO) <<<<<<<<
    log("📨 Disparando envio ao Teams (após salvar prints)")
    enviar_teams()

    time.sleep(3)

    log("📕 Fechando somente o relatório (sem salvar)")
    wb.Close(SaveChanges=False)

    log("🏁 Ciclo finalizado com sucesso")

# ================= PERGUNTA INICIAL (SEU PEDIDO) =================

resposta = input("Rodar agora? (S = rodar agora / N = aguardar virar a hora): ").strip().upper()

if resposta == "S":
    log("▶ Rodando imediatamente por comando do usuário")
    executar_automacao()
else:
    log("⏳ Aguardando virar a hora cheia...")

# ================= AGENDAMENTO =================
schedule.every(30).minutes.do(executar_automacao)

log("🤖 Robô ativo (10h às 21h)")

while True:
    schedule.run_pending()
    time.sleep(30)