import os
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich import box
import pyfiglet

console = Console()
ARQUIVO_CONFIG = os.path.expanduser("~/.devia_config.json")

def banner():
    os.system("clear")
    titulo = pyfiglet.figlet_format("DEV IA", font="slant")
    console.print(f"[bold cyan]{titulo}[/bold cyan]")
    console.print(Align.center("[bold magenta]⚙️  Configuração Inicial  ⚙️[/bold magenta]\n"))

def carregar_config():
    """Carrega configuração existente"""
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_config(config):
    """Salva configuração"""
    with open(ARQUIVO_CONFIG, "w") as f:
        json.dump(config, f, indent=2)
    os.chmod(ARQUIVO_CONFIG, 0o600)

def verificar_config():
    """Verifica se está configurado corretamente"""
    config = carregar_config()
    
    if not config.get("mistral_api_key"):
        return False, "API Key da Mistral não configurada"
    
    if not config.get("auth_url"):
        return False, "URL de autenticação não configurada"
    
    if len(config.get("mistral_api_key", "")) < 20:
        return False, "API Key parece inválida"
    
    return True, "Tudo certo!"

def configurar():
    """Wizard de configuração"""
    banner()
    
    config = carregar_config()
    
    console.print(Panel(
        "[bold white]Bem-vindo ao assistente de configuração![/bold white]\n"
        "[dim]Vamos configurar sua DEV IA em poucos passos[/dim]",
        title="[bold cyan]🚀 PRIMEIRO ACESSO[/bold cyan]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    
    console.print()
    
    # === API KEY DA MISTRAL ===
    console.print(Panel(
        "[bold yellow]📌 PASSO 1: API Key da Mistral[/bold yellow]\n\n"
        "[white]1. Acesse:[/white] [cyan]https://console.mistral.ai/[/cyan]\n"
        "[white]2. Faça login e vá em 'API Keys'[/white]\n"
        "[white]3. Clique em 'Create new key'[/white]\n"
        "[white]4. Copie a chave e cole aqui[/white]",
        border_style="yellow",
        box=box.ROUNDED
    ))
    console.print()
    
    chave_atual = config.get("mistral_api_key", "")
    if chave_atual:
        console.print(f"[dim]Chave atual: {chave_atual[:10]}...{chave_atual[-4:]}[/dim]\n")
        manter = Confirm.ask("[yellow]Manter chave atual?[/yellow]", default=True)
        if not manter:
            chave_atual = ""
    
    if not chave_atual:
        while True:
            chave = Prompt.ask("[bold blue]🔑 Cole sua API Key[/bold blue]").strip()
            if len(chave) >= 20:
                config["mistral_api_key"] = chave
                break
            console.print("[bold red]❌ Chave muito curta. Tente novamente.[/bold red]\n")
    else:
        config["mistral_api_key"] = chave_atual
    
    console.print("[bold green]✅ API Key configurada![/bold green]\n")
    
    # === URL DE AUTENTICAÇÃO ===
    console.print(Panel(
        "[bold yellow]📌 PASSO 2: URL do Sistema de Login[/bold yellow]\n\n"
        "[white]URL padrão já configurada para o Dev Shield Auth[/white]",
        border_style="yellow",
        box=box.ROUNDED
    ))
    console.print()
    
    url_padrao = "https://dev-shield-auth.base44.app/api/verificar"
    url_atual = config.get("auth_url", url_padrao)
    
    mudar = Confirm.ask(
        f"[yellow]Usar URL padrão? ({url_atual[:40]}...)[/yellow]",
        default=True
    )
    
    if mudar:
        config["auth_url"] = url_padrao
    else:
        config["auth_url"] = Prompt.ask("[bold blue]🌐 Cole a URL da API[/bold blue]").strip()
    
    console.print("[bold green]✅ URL configurada![/bold green]\n")
    
    # === MODELO PADRÃO ===
    console.print(Panel(
        "[bold yellow]📌 PASSO 3: Modelo Padrão (opcional)[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED
    ))
    console.print()
    
    modelos = {
        "1": "codestral-latest",
        "2": "mistral-large-latest",
        "3": "mistral-small-latest",
        "4": "ministral-8b-latest",
    }
    
    console.print("[white]1.[/white] Codestral (recomendado para código)")
    console.print("[white]2.[/white] Mistral Large (mais inteligente)")
    console.print("[white]3.[/white] Mistral Small (rápido)")
    console.print("[white]4.[/white] Ministral 8B (ultra rápido)")
    console.print()
    
    escolha = Prompt.ask(
        "[bold blue]Escolha o modelo padrão[/bold blue]",
        choices=["1", "2", "3", "4"],
        default="1"
    )
    config["modelo_padrao"] = modelos[escolha]
    
    # === SALVAR ===
    salvar_config(config)
    
    console.print()
    console.print(Panel(
        "[bold green]🎉 CONFIGURAÇÃO CONCLUÍDA![/bold green]\n\n"
        f"[white]✅ API Key:[/white] [green]Configurada[/green]\n"
        f"[white]✅ Auth URL:[/white] [green]{config['auth_url'][:40]}...[/green]\n"
        f"[white]✅ Modelo:[/white] [green]{config['modelo_padrao']}[/green]\n\n"
        f"[dim]Configuração salva em: {ARQUIVO_CONFIG}[/dim]",
        title="[bold magenta]✨ TUDO PRONTO[/bold magenta]",
        border_style="green",
        box=box.DOUBLE
    ))
    
    console.print("\n[bold cyan]Execute 'python login-ia.py' para começar![/bold cyan]\n")

if __name__ == "__main__":
    try:
        configurar()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]❌ Configuração cancelada![/bold red]\n")
        sys.exit(1)
