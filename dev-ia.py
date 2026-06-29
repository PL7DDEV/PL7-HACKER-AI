import requests
import json
import os
import re
import time
import threading
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.align import Align
from rich import box
import pyfiglet

# ===== CARREGAR CONFIGURAÇÃO =====
ARQUIVO_CONFIG = os.path.expanduser("~/.devia_config.json")

def carregar_config():
    """Carrega o arquivo de configuração"""
    if not os.path.exists(ARQUIVO_CONFIG):
        print("\n❌ Configuração não encontrada!")
        print("⚙️  Execute: python setup.py\n")
        sys.exit(1)
    try:
        with open(ARQUIVO_CONFIG, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"\n❌ Erro ao ler configuração: {e}")
        print("⚙️  Execute: python setup.py\n")
        sys.exit(1)

# Carregar config
CONFIG = carregar_config()
MINHA_CHAVE = CONFIG.get("mistral_api_key", "")
MODELO_PADRAO = CONFIG.get("modelo_padrao", "codestral-latest")
URL = "https://api.mistral.ai/v1/chat/completions"
PASTA_DOWNLOAD = "/storage/emulated/0/Download"

# Validar API Key
if not MINHA_CHAVE or len(MINHA_CHAVE) < 20:
    print("\n❌ API Key da Mistral inválida ou não configurada!")
    print("⚙️  Execute: python setup.py\n")
    sys.exit(1)

console = Console()

# ===== MODELOS DISPONÍVEIS NA MISTRAL =====
MODELOS = {
    "1":  {"id": "mistral-large-latest",     "nome": "Mistral Large",        "desc": "🏆 Mais inteligente"},
    "2":  {"id": "mistral-small-latest",     "nome": "Mistral Small",        "desc": "⚡ Rápido e eficiente"},
    "3":  {"id": "mistral-medium-latest",    "nome": "Mistral Medium",       "desc": "⚖️ Equilíbrio"},
    "4":  {"id": "codestral-latest",         "nome": "Codestral",            "desc": "👨‍💻 Especialista em código (TOP)"},
    "5":  {"id": "ministral-8b-latest",      "nome": "Ministral 8B",         "desc": "🚀 Ultra leve e veloz"},
    "6":  {"id": "ministral-3b-latest",      "nome": "Ministral 3B",         "desc": "💨 O mais rápido"},
    "7":  {"id": "open-mistral-nemo",        "nome": "Mistral Nemo",         "desc": "🌐 Multilíngue avançado"},
    "8":  {"id": "open-mixtral-8x22b",       "nome": "Mixtral 8x22B",        "desc": "💪 Mistura de especialistas"},
    "9":  {"id": "open-mixtral-8x7b",        "nome": "Mixtral 8x7B",         "desc": "📚 Grande contexto"},
    "10": {"id": "pixtral-large-latest",     "nome": "Pixtral Large",        "desc": "👁️ Visão computacional"},
}

# ===== TELA DE BOAS-VINDAS =====
def banner():
    os.system("clear")
    titulo = pyfiglet.figlet_format("DEV IA", font="slant")
    console.print(f"[bold cyan]{titulo}[/bold cyan]")
    console.print(Align.center("[bold magenta]✨ Assistente de Programação com Mistral AI ✨[/bold magenta]"))
    console.print(Align.center("[dim]Desenvolvido para Termux[/dim]\n"))

# ===== ENCONTRAR MODELO PADRÃO =====
def encontrar_modelo_padrao():
    """Retorna o modelo padrão definido na config"""
    for num, info in MODELOS.items():
        if info["id"] == MODELO_PADRAO:
            return num, info
    # Se não achar, retorna o primeiro
    return "4", MODELOS["4"]

# ===== MENU DE MODELOS =====
def menu_modelos():
    banner()
    
    num_padrao, modelo_padrao = encontrar_modelo_padrao()
    
    tabela = Table(
        title="🤖 [bold yellow]MODELOS MISTRAL DISPONÍVEIS[/bold yellow]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        title_style="bold yellow",
        show_lines=True
    )
    tabela.add_column("Nº", style="bold green", justify="center", width=4)
    tabela.add_column("Modelo", style="bold white", width=24)
    tabela.add_column("Descrição", style="italic cyan")

    for num, info in MODELOS.items():
        nome = info["nome"]
        if num == num_padrao:
            nome += " ⭐"
        tabela.add_row(num, nome, info["desc"])

    console.print(tabela)
    console.print(f"\n[dim]⭐ = Modelo padrão configurado[/dim]\n")

    escolha = Prompt.ask(
        "[bold yellow]🎯 Escolha um modelo[/bold yellow]",
        choices=list(MODELOS.keys()),
        default=num_padrao
    )
    
    modelo = MODELOS[escolha]
    console.print(f"\n[bold green]✅ Modelo selecionado:[/bold green] [bold cyan]{modelo['nome']}[/bold cyan]\n")
    time.sleep(1)
    return modelo

# ===== EXTRAIR CÓDIGO DA RESPOSTA =====
def extrair_codigos(texto):
    padrao = r"```(\w+)?\n(.*?)```"
    return re.findall(padrao, texto, re.DOTALL)

# ===== SALVAR CÓDIGO NA PASTA DOWNLOAD =====
def salvar_codigo(linguagem, codigo):
    extensoes = {
        "python": "py", "py": "py",
        "javascript": "js", "js": "js",
        "html": "html", "css": "css",
        "java": "java", "c": "c",
        "cpp": "cpp", "c++": "cpp",
        "bash": "sh", "shell": "sh", "sh": "sh",
        "php": "php", "ruby": "rb",
        "go": "go", "rust": "rs",
        "kotlin": "kt", "swift": "swift",
        "typescript": "ts", "ts": "ts",
        "json": "json", "xml": "xml",
        "sql": "sql", "yaml": "yml",
        "lua": "lua", "dart": "dart",
    }
    
    ext = extensoes.get(linguagem.lower() if linguagem else "", "txt")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"devia_{timestamp}.{ext}"
    
    if not os.path.exists(PASTA_DOWNLOAD):
        os.makedirs(PASTA_DOWNLOAD, exist_ok=True)
    
    caminho = os.path.join(PASTA_DOWNLOAD, nome_arquivo)
    
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(codigo)
    
    return caminho, nome_arquivo

# ===== ANIMAÇÃO DE PROCESSAMENTO =====
def animar_processamento():
    return [
        "🧠 Analisando sua solicitação...",
        "💭 Pensando na melhor solução...",
        "⚙️  Estruturando o código...",
        "✨ Aplicando as melhores práticas...",
        "🔍 Revisando a lógica...",
        "📝 Finalizando a resposta..."
    ]

# ===== CHAMAR API =====
def chamar_api(modelo_id, historico):
    headers = {
        "Authorization": f"Bearer {MINHA_CHAVE}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": modelo_id,
        "messages": historico,
        "temperature": 0.7,
        "max_tokens": 4096
    }
    
    response = requests.post(URL, headers=headers, json=payload, timeout=90)
    return response.json()

# ===== EXIBIR RESPOSTA BONITA =====
def exibir_resposta(resposta, modelo_nome):
    console.print()
    md = Markdown(resposta)
    painel = Panel(
        md,
        title=f"[bold cyan]🤖 {modelo_nome}[/bold cyan]",
        title_align="left",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(painel)

# ===== MENU DE COMANDOS =====
def mostrar_ajuda():
    tabela = Table(title="📚 [bold yellow]COMANDOS DISPONÍVEIS[/bold yellow]", box=box.ROUNDED, border_style="magenta")
    tabela.add_column("Comando", style="bold green")
    tabela.add_column("Descrição", style="white")
    
    tabela.add_row("/sair", "Encerra o programa")
    tabela.add_row("/limpar", "Limpa o histórico da conversa")
    tabela.add_row("/modelo", "Troca o modelo de IA")
    tabela.add_row("/tela", "Limpa a tela")
    tabela.add_row("/config", "Reconfigurar o sistema")
    tabela.add_row("/info", "Mostra informações da conta")
    tabela.add_row("/ajuda", "Mostra esta mensagem")
    
    console.print(tabela)

# ===== MOSTRAR INFO =====
def mostrar_info(modelo):
    info = Panel(
        f"[bold white]🔑 API Key:[/bold white] [green]{MINHA_CHAVE[:10]}...{MINHA_CHAVE[-4:]}[/green]\n"
        f"[bold white]🤖 Modelo Atual:[/bold white] [cyan]{modelo['nome']}[/cyan]\n"
        f"[bold white]⭐ Modelo Padrão:[/bold white] [yellow]{MODELO_PADRAO}[/yellow]\n"
        f"[bold white]📁 Pasta de Saída:[/bold white] [magenta]{PASTA_DOWNLOAD}[/magenta]\n"
        f"[bold white]⚙️  Arquivo Config:[/bold white] [dim]{ARQUIVO_CONFIG}[/dim]",
        title="[bold cyan]ℹ️  INFORMAÇÕES DO SISTEMA[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED
    )
    console.print(info)

# ===== LOOP PRINCIPAL =====
def chat_ia():
    # Iniciar com o modelo padrão configurado
    num_padrao, modelo = encontrar_modelo_padrao()
    
    # Perguntar se quer usar o padrão ou escolher outro
    banner()
    console.print(Panel(
        f"[bold green]🎯 Modelo padrão configurado:[/bold green] [cyan]{modelo['nome']}[/cyan]\n"
        f"[dim]{modelo['desc']}[/dim]",
        title="[bold yellow]MODELO PADRÃO[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED
    ))
    console.print()
    
    usar_padrao = Prompt.ask(
        "[bold yellow]Usar modelo padrão?[/bold yellow]",
        choices=["s", "n"],
        default="s"
    )
    
    if usar_padrao == "n":
        modelo = menu_modelos()
    
    historico = [{
        "role": "system",
        "content": (
            "Você é um assistente de programação expert e amigável. "
            "Sempre forneça códigos limpos, organizados e bem comentados em português. "
            "Use blocos de código markdown com a linguagem especificada (ex: ```python). "
            "Explique brevemente o que o código faz antes de apresentá-lo."
        )
    }]
    
    banner()
    console.print(Panel(
        f"[bold green]✅ Conectado ao modelo:[/bold green] [cyan]{modelo['nome']}[/cyan]\n"
        f"[bold yellow]📁 Códigos serão salvos em:[/bold yellow] [white]{PASTA_DOWNLOAD}[/white]\n"
        f"[dim]Digite /ajuda para ver os comandos disponíveis[/dim]",
        title="[bold magenta]🚀 SISTEMA PRONTO[/bold magenta]",
        border_style="green",
        box=box.DOUBLE
    ))
    
    while True:
        console.print()
        try:
            user_input = Prompt.ask("[bold blue]💬 Você[/bold blue]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold magenta]👋 Até logo![/bold magenta]\n")
            break
        
        if not user_input:
            continue
        
        # Comandos
        cmd = user_input.lower()
        if cmd == "/sair":
            console.print("\n[bold magenta]👋 Até logo! Bons códigos![/bold magenta]\n")
            break
        if cmd == "/limpar":
            historico = [historico[0]]
            console.print("[bold yellow]🧹 Histórico limpo com sucesso![/bold yellow]")
            continue
        if cmd == "/modelo":
            modelo = menu_modelos()
            continue
        if cmd == "/tela":
            banner()
            continue
        if cmd == "/ajuda":
            mostrar_ajuda()
            continue
        if cmd == "/info":
            mostrar_info(modelo)
            continue
        if cmd == "/config":
            console.print("\n[bold cyan]⚙️  Abrindo configuração...[/bold cyan]\n")
            time.sleep(1)
            os.system("python setup.py")
            console.print("\n[bold yellow]🔄 Reinicie a IA para aplicar as mudanças![/bold yellow]\n")
            sys.exit(0)
        
        historico.append({"role": "user", "content": user_input})
        
        mensagens = animar_processamento()
        
        try:
            resultado = {}
            
            def fazer_request():
                try:
                    resultado["data"] = chamar_api(modelo["id"], historico)
                except Exception as e:
                    resultado["erro"] = str(e)
            
            with Progress(
                SpinnerColumn(spinner_name="dots", style="cyan"),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task(mensagens[0], total=None)
                
                thread = threading.Thread(target=fazer_request)
                thread.start()
                
                idx = 0
                while thread.is_alive():
                    progress.update(task, description=f"[bold cyan]{mensagens[idx % len(mensagens)]}[/bold cyan]")
                    time.sleep(0.8)
                    idx += 1
                
                thread.join()
            
            if "erro" in resultado:
                raise Exception(resultado["erro"])
            
            data = resultado["data"]
            
            if "choices" in data:
                resposta = data["choices"][0]["message"]["content"]
                historico.append({"role": "assistant", "content": resposta})
                
                exibir_resposta(resposta, modelo["nome"])
                
                # Mostrar tokens usados (se disponível)
                if "usage" in data:
                    usage = data["usage"]
                    console.print(
                        f"[dim]📊 Tokens: {usage.get('prompt_tokens', 0)} entrada + "
                        f"{usage.get('completion_tokens', 0)} saída = "
                        f"{usage.get('total_tokens', 0)} total[/dim]"
                    )
                
                # Extrair e salvar códigos
                codigos = extrair_codigos(resposta)
                if codigos:
                    console.print()
                    console.print(Panel(
                        f"[bold green]🎉 {len(codigos)} bloco(s) de código detectado(s)![/bold green]",
                        border_style="green",
                        box=box.ROUNDED
                    ))
                    
                    for i, (lang, code) in enumerate(codigos, 1):
                        with console.status(f"[bold yellow]💾 Salvando arquivo {i}...[/bold yellow]", spinner="dots"):
                            time.sleep(0.5)
                            caminho, nome = salvar_codigo(lang, code.strip())
                        
                        console.print(Panel(
                            f"[bold white]📄 Arquivo:[/bold white] [cyan]{nome}[/cyan]\n"
                            f"[bold white]📂 Local:[/bold white] [yellow]{caminho}[/yellow]\n"
                            f"[bold white]🔤 Linguagem:[/bold white] [magenta]{lang or 'texto'}[/magenta]",
                            title=f"[bold green]✅ CÓDIGO {i} SALVO[/bold green]",
                            border_style="green",
                            box=box.ROUNDED
                        ))
            else:
                erro = data.get("message", data.get("error", {}).get("message", str(data)))
                console.print(Panel(
                    f"[bold red]{erro}[/bold red]",
                    title="[bold red]❌ ERRO DA API[/bold red]",
                    border_style="red"
                ))
                historico.pop()
        
        except requests.exceptions.Timeout:
            console.print("[bold red]⏱️  Tempo esgotado! Tente novamente.[/bold red]")
            historico.pop()
        except Exception as e:
            console.print(Panel(
                f"[bold red]{str(e)}[/bold red]",
                title="[bold red]❌ ERRO[/bold red]",
                border_style="red"
            ))
            historico.pop()

if __name__ == "__main__":
    try:
        chat_ia()
    except KeyboardInterrupt:
        console.print("\n\n[bold magenta]👋 Programa encerrado pelo usuário![/bold magenta]\n")
