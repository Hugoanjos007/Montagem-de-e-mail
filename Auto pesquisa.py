import os
import shutil
from xml.dom.xmlbuilder import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import datetime as dt
#==================================Configurações===============================
login = "hugo.anjos"
senha_snx = "Fort2022@"
PASTA_TEMP_DOWNLOAD = r"C:\Temp\downloads_crm"
PASTA_RELATORIO_1 = r"\\192.168.15.102\e\CaeduADM\RELATÓRIOS\2025\04.Abril\powerquery\pesquisa hr a hr relatorio chamada"
PASTA_RELATORIO_2 = r"\\192.168.15.102\e\CaeduADM\RELATÓRIOS\2025\04.Abril\powerquery\ura satisfaçao pesquisa analitica"
PASTA_RELATORIO_3 = r"\\192.168.15.102\e\CaeduADM\RELATÓRIOS\2025\04.Abril\powerquery\SMS"
#================================URL's========================================
relatorio_pesquisa = "http://192.168.15.220/crm/index.php?codmodulo=446"
relatorio_chamadas = "http://192.168.15.220/crm/index.php?codmodulo=389"
relatorio_sms = "http://192.168.15.220/crm/index.php?codmodulo=516"
smart_loguin = "http://192.168.15.220/crm/index.php?codmodulo=446"
def feito(msg):
    print(f"[{dt.datetime.now().strftime('%d/%m %H:%M:%S')}] {msg}")
#Limpando as pastas de destino
def limpar_pasta(pasta):
    os.makedirs(pasta, exist_ok=True)
    for f in os.listdir(pasta):
        caminho = os.path.join(pasta, f)
        if os.path.isfile(caminho):
            try:
                os.remove(caminho)
            except:
                pass
#baixar os relatorios
def baixar_relatorios():
    limpar_pasta(PASTA_RELATORIO_1)
    feito("Pasta 1 limpa.")
    limpar_pasta(PASTA_RELATORIO_2)
    feito("Pasta 2 limpa.")
    limpar_pasta(PASTA_RELATORIO_3)
    feito("Pasta 3 limpa.")    
    feito("Iniciando o processo de download dos relatórios.")
    snx = webdriver.Chrome()
    snx.get(smart_loguin)
    #definindo os elementos de login
    usuario = snx.find_element("id", "l_login")
    senha = snx.find_element("id", "l_senha")
    enter_button = snx.find_element("class name", "fourth-container-button")
    #clicando nos elementos e inserindo os dados de login
    usuario.click()
    usuario.send_keys(login)
    senha.click()
    senha.send_keys(senha_snx)
    enter_button.click()
    time.sleep(5)
    feito("Acessando o relatório de pesquisa.")
    snx.get(relatorio_pesquisa)
    exportar = snx.find_element("id", "btn_excel")
    exportar.click()
    feito("Dowload do relatório de Pesquisa concluído.")
    snx.get(relatorio_chamadas)
    buscar_botton = snx.find_element("id", "btn_pesquisar")
    buscar_botton.click()
    time.sleep(5)
    exportar = snx.find_element("id", "btn_excel")
    exportar.click()
    feito("Dowload do relatório de Chamadas concluído.")
    snx.get(relatorio_sms)
    agrupar = WebDriverWait(snx, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "jqTransformSelectOpen")))
    agrupar.click()
    opcao = WebDriverWait(snx, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@index='0']")))
    opcao.click()
    buscar_botton = snx.find_element("id", "btn_pesquisar")
    buscar_botton.click()
    time.sleep(3)
    exportar = snx.find_element("id", "btn_excel")
    exportar.click()
    feito("Dowload do relatório de SMS concluído.")
baixar_relatorios()