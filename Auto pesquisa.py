from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
import time as tm
#==================UTILITARIOS=========================
relatorio_pesquisa = "http://192.168.15.220/crm/index.php?codmodulo=446"
relatorio_chamadas = "http://192.168.15.220/crm/index.php?codmodulo=389"
relatorio_sms = "http://192.168.15.220/crm/index.php?codmodulo=516"
#baixar os relatorios
def baixar_relatorios():
    snx = webdriver.Chrome()
    snx.get("http://192.168.15.220/crm/index.php?codmodulo=446")
    #definindo os elementos de login
    usuario = snx.find_element("id", "l_login")
    senha = snx.find_element("id", "l_senha")
    enter_button = snx.find_element("class name", "fourth-container-button")
    #clicando nos elementos e inserindo os dados de login
    usuario.click()
    usuario.send_keys("hugo.anjos")
    senha.click()
    senha.send_keys("Fort2022@")
    enter_button.click()
    tm.sleep(5)
    snx.get(relatorio_pesquisa)
    exportar = snx.find_element("id", "btn_excel")
    exportar.click()
    snx.get(relatorio_chamadas)
    buscar_botton = snx.find_element("id", "btn_pesquisar")
    buscar_botton.click()
    tm.sleep(3)
    exportar = snx.find_element("id", "btn_excel")
    exportar.click()
    snx.get(relatorio_sms)
    agrupar_list = snx.find_element("class name", "jqTransformSelectOpen")
    agrupar_list.click()
    index_0 = snx.find_element("index", "0")
    index_0.click()
    tm.sleep(30)
baixar_relatorios()