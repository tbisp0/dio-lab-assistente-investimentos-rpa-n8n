import requests
from bs4 import BeautifulSoup
import sys

URL_PAGINA = "https://digitalinnovationone.github.io/dio-lab-assistente-investimentos-rpa-n8n/"

# Permite passar a URL do webhook como argumento de linha de comando ou usar a padrão
if len(sys.argv) > 1:
    N8N_WEBHOOK = sys.argv[1]
else:
    N8N_WEBHOOK = "http://localhost:5678/webhook-test/Clientes"

print(f"[*] 1. Baixando clientes de: {URL_PAGINA}")
try:
    resp_html = requests.get(URL_PAGINA, timeout=30)
    resp_html.raise_for_status()
except Exception as e:
    print(f"[!] Erro ao acessar página de clientes: {e}")
    sys.exit(1)

print("[*] 2. Extraindo clientes da tabela HTML (BeautifulSoup)...")
soup = BeautifulSoup(resp_html.text, "html.parser")
linhas = soup.select("#clientes tbody tr")

clientes = []
for linha in linhas:
    colunas = linha.find_all("td")
    if len(colunas) >= 4:
        cliente = {
            "nome": colunas[0].get_text(strip=True),
            "email": colunas[1].get_text(strip=True),
            "saldo": colunas[2].get_text(strip=True),
            "perfil": colunas[3].get_text(strip=True),
        }
        clientes.append(cliente)

print(f"[+] Total de clientes encontrados: {len(clientes)}")
for c in clientes:
    print(f"    - {c['nome']} ({c['perfil']}) | Saldo: {c['saldo']} | Email: {c['email']}")

print(f"\n[*] 3. Disparando POST para o Webhook do n8n: {N8N_WEBHOOK}")
payload = {"clientes": clientes}

try:
    resp = requests.post(
        N8N_WEBHOOK,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    print(f"[+] Status Code: {resp.status_code}")
    print(f"[+] Resposta do n8n:\n{resp.text}")
except Exception as e:
    print(f"[!] Erro ao conectar no Webhook do n8n: {e}")
    print("    Dica: Verifique se o n8n está aberto e se você clicou no botão 'Listen for test event' no nó Webhook.")
