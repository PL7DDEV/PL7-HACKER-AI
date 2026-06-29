import requests
import json
import os
import hashlib
import platform
import subprocess
import time
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
import pyfiglet

# ===== CONFIGURAÇÃO =====
ARQUIVO_CONFIG = os.path.expanduser("~/.devia_config.json")
ARQUIVO_SESSAO = os.path.expanduser("~/.devia_session")

console = Console()

# ===== VERIFICAR CONFIGURAÇÃO =====
def verificar_configuracao():
    """Verifica se o sistema está configurado"""
    if not os.path.exists(ARQUIVO_CONFIG):
        return False, "Arquivo de configuração não encontrado"
    
    try:
        with open(ARQUIVO_CONFIG, "r") as f:
            config = json.load(f)
        
        if not config.get("mistral_api_key"):
            return False, "API Key da Mistral não configurada"
        
        if not config.get("auth_url"):
            return False, "URL de autenticação não configurada"
        
        if len(config.get("mistral_api_key", "")) < 20:
            return False, "API Key inválida"
        
        return True, config
    except Exception as e:
        return False, f"Erro ao ler configuração: {e}"

def tela_sem_config(motivo):
    """Mostra tela quando não está configurado"""
    os.system("clear")
    titulo = pyfiglet.figlet_format("DEV IA", font="slant")
    console.print(f"[bold red]{titulo}[/bold red]")
    
    console.print(Panel(
        f"[bold red]⚠️  SISTEMA NÃO CONFIGURADO[/bold red]\n\n"
        f"[white]Motivo:[/white] [yellow]{motivo}[/yellow]\n\n"
        f"[bold cyan]Execute o comando abaixo para configurar:[/bold cyan]\n"
        f"[bold green]python setup.py[/bold green]",
        title="[bold red]❌ ERRO DE CONFIGURAÇÃO[/bold red]",
        border_style="red",
        box=box.DOUBLE
    ))
    
    console.print()
    rodar = Confirm.ask("[bold yellow]Deseja executar a configuração agora?[/bold yellow]", default=True)
    
    if rodar:
        console.print("\n[bold cyan]🚀 Iniciando configuração...[/bold cyan]\n")
        time.sleep(1)
        os.system("python setup.py")
        sys.exit(0)
    else:
        console.print("\n[bold red]❌ Configure o sistema antes de continuar![/bold red]\n")
        sys.exit(1)

# ===== GERAR HWID ÚNICO =====
def gerar_hwid():
    """Gera ID único do dispositivo"""
    try:
        info = []
        for prop in ["ro.serialno", "ro.product.model", "ro.build.fingerprint"]:
            try:
                val = subprocess.check_output(
                    ["getprop", prop], 
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                if val:
                    info.append(val)
            except:
                pass
        
        info.append(platform.node())
        info.append(platform.machine())
        
        texto = "|".join(info)
        return hashlib.sha256(texto.encode()).hexdigest()
    except:
        return hashlib.sha256(platform.node().encode()).hexdigest()

# ===== BANNER =====
def banner():
    os.system("clear")
    titulo = pyfiglet.figlet_format("DEV IA", font="slant")
    console.print(f"[bold cyan]{titulo}[/bold cyan]")
    console.print(Align.center("[bold magenta]🛡️  Dev Shield Auth System  🛡️[/bold magenta]\n"))

# ===== SESSÃO =====
def salvar_sessao(username, password):
    try:
        dados = {
            "username": username,
            "password": password,
            "data": datetime.now().isoformat()
        }
        with open(ARQUIVO_SESSAO, "w") as f:
            json.dump(dados, f)
        os.chmod(ARQUIVO_SESSAO, 0o600)
    except:
        pass

def carregar_sessao():
    try:
        if os.path.exists(ARQUIVO_SESSAO):
            with open(ARQUIVO_SESSAO, "r") as f:
                return json.load(f)
    except:
        pass
    return None

def deletar_sessao():
    try:
        if os.path.exists(ARQUIVO_SESSAO):
            os.remove(ARQUIVO_SESSAO)
    except:
        pass

# ===== VERIFICAR LOGIN =====
def verificar_login(username, password, auth_url):
    hwid = gerar_hwid()
    
    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[bold cyan]🔐 Verificando credenciais...[/bold cyan]"),
        transient=True,
    ) as progress:
        progress.add_task("verificando", total=None)
        
        try:
            response = requests.get(
                auth_url,
                params={
                    "username": username,
                    "password": password,
                    "hwid": hwid
                },
                timeout=15
            )
            return response.json()
        except requests.exceptions.Timeout:
            return {"sucesso": False, "mensagem": "⏱️ Tempo esgotado"}
        except requests.exceptions.ConnectionError:
            return {"sucesso": False, "mensagem": "🌐 Sem conexão"}
        except Exception as e:
            return {"sucesso": False, "mensagem": f"❌ Erro: {str(e)}"}

# ===== TELA DE LOGIN =====
def tela_login(config):
    banner()
    auth_url = config["auth_url"]
    
    # Tenta login automático
    sessao = carregar_sessao()
    if sessao:
        console.print(Panel(
            f"[bold green]🔄 Sessão salva encontrada[/bold green]\n"
            f"[white]Usuário:[/white] [cyan]{sessao['username']}[/cyan]",
            title="[bold yellow]LOGIN AUTOMÁTICO[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED
        ))
        
        usar = Confirm.ask("[bold yellow]Usar login salvo?[/bold yellow]", default=True)
        
        if usar:
            resultado = verificar_login(sessao["username"], sessao["password"], auth_url)
            if resultado.get("sucesso"):
                return resultado, sessao["username"]
            else:
                console.print(f"\n[bold red]❌ {resultado.get('mensagem', 'Erro')}[/bold red]")
                deletar_sessao()
                time.sleep(2)
    
    # Login manual
    while True:
        banner()
        
        console.print(Panel(
            "[bold white]Digite suas credenciais para acessar a DEV IA[/bold white]\n"
            "[dim]Não tem conta? Entre em contato com o admin[/dim]",
            title="[bold cyan]🔐 LOGIN[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        ))
        console.print()
        
        username = Prompt.ask("[bold blue]👤 Usuário[/bold blue]").strip()
        password = Prompt.ask("[bold blue]🔒 Senha[/bold blue]", password=True).strip()
        
        if not username or not password:
            console.print("[bold red]❌ Preencha todos os campos![/bold red]")
            time.sleep(2)
            continue
        
        resultado = verificar_login(username, password, auth_url)
        
        if resultado.get("sucesso"):
            console.print()
            salvar = Confirm.ask("[bold yellow]💾 Salvar login?[/bold yellow]", default=True)
            if salvar:
                salvar_sessao(username, password)
            return resultado, username
        else:
            console.print()
            console.print(Panel(
                f"[bold red]{resultado.get('mensagem', 'Credenciais inválidas')}[/bold red]",
                title="[bold red]❌ ACESSO NEGADO[/bold red]",
                border_style="red",
                box=box.ROUNDED
            ))
            
            tentar = Confirm.ask("\n[bold yellow]Tentar novamente?[/bold yellow]", default=True)
            if not tentar:
                console.print("\n[bold magenta]👋 Até logo![/bold magenta]\n")
                sys.exit(0)

# ===== BOAS-VINDAS =====
def tela_boasvindas(dados, username):
    banner()
    
    plano = dados.get("plano", "free").upper()
    validade = dados.get("validade", "Vitalício")
    
    cores = {"FREE": "white", "VIP": "yellow", "PREMIUM": "magenta"}
    emojis = {"FREE": "🆓", "VIP": "⭐", "PREMIUM": "💎"}
    cor = cores.get(plano, "white")
    emoji = emojis.get(plano, "👤")
    
    console.print(Panel(
        f"[bold green]✅ LOGIN REALIZADO COM SUCESSO![/bold green]\n\n"
        f"[bold white]👤 Usuário:[/bold white] [cyan]{username}[/cyan]\n"
        f"[bold white]{emoji} Plano:[/bold white] [bold {cor}]{plano}[/bold {cor}]\n"
        f"[bold white]📅 Válido até:[/bold white] [yellow]{validade}[/yellow]\n"
        f"[bold white]🔐 HWID:[/bold white] [dim]{gerar_hwid()[:20]}...[/dim]",
        title="[bold magenta]🎉 BEM-VINDO[/bold magenta]",
        border_style="green",
        box=box.DOUBLE
    ))
    
    console.print("\n[bold cyan]🚀 Carregando a IA...[/bold cyan]")
    time.sleep(2)

# ===== INICIAR IA =====
def iniciar_ia():
    try:
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dev-ia.py")
        if os.path.exists(caminho):
            os.system(f"python {caminho}")
        else:
            os.system("python dev-ia.py")
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")

# ===== MAIN =====
if __name__ == "__main__":
    try:
        # VERIFICA SE ESTÁ CONFIGURADO
        ok, resultado = verificar_configuracao()
        
        if not ok:
            tela_sem_config(resultado)
        
        config = resultado
        dados, username = tela_login(config)
        tela_boasvindas(dados, username)
        iniciar_ia()
    except KeyboardInterrupt:
        console.print("\n\n[bold magenta]👋 Programa encerrado![/bold magenta]\n")
        sys.exit(0)
