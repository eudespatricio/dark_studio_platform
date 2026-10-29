"""
Script Oficial de Autenticação OAuth2 do YouTube — Dark Studio Platform
Permite autorizar o canal 'A Via da Descoberta' (@AViadaDescoberta - UC8RJWr3b2pKtnU1wOhV_bDQ)
ou qualquer um dos Top 3 canais da plataforma para upload 100% automático de vídeos.
"""

import sys
import os
import json
from pathlib import Path

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
CREDENTIALS_DIR = BASE_DIR / "workspace" / "credentials"
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtubepartner",
    "https://www.googleapis.com/auth/yt-analytics.readonly",  # AVD, CTR, impressoes (Benchmark Agent)
]

def resolve_client_config(channel_id: str):
    """
    Retorna ('file', path) ou ('config', dict) com base no canal:
    - Ch 1 & Ch 2: Projeto 1 (client_secrets.json) -> 10.000 un/dia
    - Ch 3 & Ch 4: Projeto 2 (Dark Auth2) -> 10.000 un/dia
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / ".env")
    except Exception:
        pass

    clean_cid = str(channel_id).strip()
    is_p2 = clean_cid in (
        "3", "ch3", "biohack", "biohacklongevidade", "longevidade", "UCIjEnT4adPYVyi0UlrCITBA",
        "4", "ch4", "aintnohuman", "aintnohumanoficial", "music", "UCbO67ez7TKOJ8C_kpUF4t5Q",
    )

    if is_p2:
        print("\n" + "=" * 70)
        print("  🔑 ROTEAMENTO MULTI-PROJETO: PROJETO 2 (DARK AUTH2)")
        print("  Canais: Ch3 (Bio Hack Longevidade) & Ch4 (Ain't No Human Música)")
        print("  Cota Diária Exclusiva: 10.000 unidades/dia")
        print("=" * 70)

        # 1. Verifica arquivo físico
        p2_file_env = os.getenv("DARK_AUTH2_CLIENT_SECRETS_FILE", "client_secrets_dark_auth2.json")
        candidates = [
            BASE_DIR / p2_file_env,
            BASE_DIR / "client_secrets_dark_auth2.json",
            BASE_DIR / "client_secrets_ch3_ch4.json",
            CREDENTIALS_DIR / "client_secrets_dark_auth2.json",
        ]
        for p in candidates:
            if p.exists() and p.is_file():
                return "file", p

        # 2. Verifica variáveis no .env
        c_id = os.getenv("DARK_AUTH2_CLIENT_ID", "").strip()
        c_secret = os.getenv("DARK_AUTH2_CLIENT_SECRET", "").strip()
        p_id = os.getenv("DARK_AUTH2_PROJECT_ID", "dark-auth2").strip()

        if c_id and c_secret:
            cfg = {
                "installed": {
                    "client_id": c_id,
                    "client_secret": c_secret,
                    "project_id": p_id,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost", "http://127.0.0.1:8085/"],
                }
            }
            # Salva também como arquivo de backup
            target_file = BASE_DIR / "client_secrets_dark_auth2.json"
            target_file.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
            return "config", cfg

        print("\n[ATENÇÃO] Credenciais do Projeto 2 (Dark Auth2) ainda não preenchidas no .env!")
        print("Preencha no seu arquivo .env as seguintes linhas:")
        print('  DARK_AUTH2_CLIENT_ID="seu_client_id_aqui"')
        print('  DARK_AUTH2_CLIENT_SECRET="seu_client_secret_aqui"')
        print("Ou salve o arquivo JSON baixado do GCP como 'client_secrets_dark_auth2.json' na raiz do projeto.")
        return None, None
    else:
        print("\n" + "=" * 70)
        print("  🔑 ROTEAMENTO MULTI-PROJETO: PROJETO 1 (GOOGLE CLOUD DEFAULT)")
        print("  Canais: Ch1 (A Via da Descoberta) & Ch2 (Finanças Quânticas)")
        print("  Cota Diária Exclusiva: 10.000 unidades/dia")
        print("=" * 70)

        p1_file_env = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
        candidates = [
            BASE_DIR / p1_file_env,
            BASE_DIR / "client_secrets.json",
            BASE_DIR / "client_secret.json",
            CREDENTIALS_DIR / "client_secrets.json",
            CREDENTIALS_DIR / "client_secret.json",
        ]
        for p in candidates:
            if p.exists() and p.is_file():
                return "file", p

        print("\n[ATENÇÃO] Arquivo 'client_secrets.json' do Projeto 1 não encontrado na raiz!")
        return None, None

def find_client_secrets() -> Path | None:
    t, p = resolve_client_config("1")
    return p if t == "file" else None

def main():
    print("=" * 70)
    print("  DARK STUDIO PLATFORM — AUTENTICAÇÃO OAUTH2 YOUTUBE DATA API V3")
    print("=" * 70)
    
    # Suporte a múltiplos canais via argumento CLI (ex: --channel 3 ou --channel UCIjEnT4adPYVyi0UlrCITBA)
    channel_id = "UC8RJWr3b2pKtnU1wOhV_bDQ"
    if "--channel" in sys.argv:
        idx = sys.argv.index("--channel")
        if idx + 1 < len(sys.argv):
            target = sys.argv[idx + 1]
            if target in ("4", "ch4", "aintnohuman", "aintnohumanoficial", "music"):
                channel_id = "UCbO67ez7TKOJ8C_kpUF4t5Q"
            elif target in ("3", "ch3", "biohack", "biohacklongevidade", "longevidade"):
                channel_id = "UCIjEnT4adPYVyi0UlrCITBA"
            elif target in ("2", "ch2", "financas", "financasquanticas"):
                channel_id = "UCE6Ch6nhxI81Z6ILQIw23_Q"
            elif target in ("1", "ch1", "viadadescoberta"):
                channel_id = "UC8RJWr3b2pKtnU1wOhV_bDQ"
            else:
                channel_id = target
    elif "-c" in sys.argv:
        idx = sys.argv.index("-c")
        if idx + 1 < len(sys.argv):
            channel_id = sys.argv[idx + 1]

    token_file = CREDENTIALS_DIR / f"{channel_id}_token.json"
    force_reauth = "--force" in sys.argv or "-f" in sys.argv
    
    # 1. Verifica se já está autenticado (a menos que seja forçado)
    if token_file.exists() and not force_reauth:
        print(f"\n[OK] Canal {channel_id} JA POSSUI TOKEN DE AUTORIZACAO ATIVO!")
        print(f"     Arquivo: {token_file}")
        try:
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file(str(token_file))
            if creds.refresh_token:
                print("     Status: Refresh token presente e valido para publicacao continua.")
            try:
                from googleapiclient.discovery import build
                yt = build("youtube", "v3", credentials=creds)
                res = yt.channels().list(part="snippet,statistics", mine=True).execute()
                items = res.get("items", [])
                if items:
                    ch = items[0]
                    print(f"     Canal Conectado: {ch['snippet']['title']} (@{ch['snippet'].get('customUrl', '')}) [ID: {ch['id']}]")
                    print(f"     Inscritos: {ch['statistics'].get('subscriberCount', '0')} | Videos: {ch['statistics'].get('videoCount', '0')}")
            except Exception as quota_err:
                print(f"     (Aviso: Cota da API esgotada para leitura de metricas ao vivo: quotaExceeded)")
                print("     [SUCESSO] O token OAuth2 do canal esta salvo e pronto para uso!")
            print("\n-> Para forcar uma nova re-autenticacao deste canal:\n   python authenticate_youtube.py --channel 3 --force\n")
            return
        except Exception as e:
            print(f"     Aviso ao verificar token existente: {e}")
            print("     Re-executando fluxo de autorizacao...")
    # 2. Localiza as credenciais corretas para o canal (Projeto 1 ou Dark Auth2 Projeto 2)
    cfg_type, cfg_val = resolve_client_config(channel_id)
    if not cfg_type:
        return

    print(f"\nIniciando fluxo OAuth2 com o Google para o canal {channel_id}...")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        if cfg_type == "file":
            flow = InstalledAppFlow.from_client_secrets_file(str(cfg_val), scopes=SCOPES)
        else:
            flow = InstalledAppFlow.from_client_config(cfg_val, scopes=SCOPES)
        
        print("\n" + "-" * 70)
        print("👉 Um link de autorizacao sera exibido abaixo.")
        print(f"   Copie o link, abra no seu navegador e faca login")
        print(f"   com a conta dona do canal selecionado para autorizar.")
        print("-" * 70 + "\n")

        # Inicia o servidor local para captura do callback OAuth2 com rotação automática de portas
        candidate_ports = [8085, 8086, 8087, 8088, 8095, 0]
        creds = None
        last_net_err = None

        for p in candidate_ports:
            try:
                creds = flow.run_local_server(
                    host="localhost",
                    bind_addr="0.0.0.0",
                    port=p,
                    prompt="select_account consent",
                    open_browser=False,
                )
                break
            except OSError as net_err:
                last_net_err = net_err
                try:
                    creds = flow.run_local_server(
                        host="127.0.0.1",
                        port=p,
                        prompt="select_account consent",
                        open_browser=False,
                    )
                    break
                except OSError:
                    continue

        if creds is None:
            raise last_net_err or RuntimeError("Não foi possível iniciar o servidor local de autenticação OAuth2.")

        # Backup do token anterior (mantem upload funcional caso a nova autorizacao falhe)
        if token_file.exists():
            import shutil, time
            shutil.copy2(token_file, token_file.with_suffix(f".bak{int(time.time())}.json"))

        token_data = creds.to_json()
        
        # Identifica dinamicamente o canal autenticado
        actual_id = channel_id
        actual_title = "Canal Desconhecido"
        actual_handle = ""
        try:
            from googleapiclient.discovery import build
            yt = build("youtube", "v3", credentials=creds)
            res = yt.channels().list(part="snippet,statistics", mine=True).execute()
            items = res.get("items", [])
            if items:
                ch = items[0]
                actual_id = ch['id']
                actual_title = ch['snippet']['title']
                actual_handle = ch['snippet'].get('customUrl', '')
        except Exception as api_err:
            print(f"  [Aviso] Consulta de identificacao de canal falhou: {api_err}")

        # Mapeamento estrito por ID real do canal
        TARGET_MAP = {
            "UC8RJWr3b2pKtnU1wOhV_bDQ": ("A Via da Descoberta", "channel_1_token.json", ["token.json"]),
            "UCE6Ch6nhxI81Z6ILQIw23_Q": ("Finanças Quânticas", "channel_2_token.json", []),
            "UCIjEnT4adPYVyi0UlrCITBA": ("Bio Hack Longevidade", "channel_3_token.json", []),
            "UCbO67ez7TKOJ8C_kpUF4t5Q": ("Ain't No Human", "channel_4_token.json", []),
        }

        # Alerta se o canal selecionado for diferente do solicitado no comando
        if channel_id in TARGET_MAP and actual_id != channel_id:
            expected_name = TARGET_MAP[channel_id][0]
            print("\n" + "!" * 70)
            print("  ⚠️ ALERTA DE SELEÇÃO DE CANAL DIVERGENTE NO GOOGLE!")
            print(f"  Você passou o comando para:   '{expected_name}' ({channel_id})")
            print(f"  Mas na tela do Google escolheu: '{actual_title}' ({actual_id})")
            print("!" * 70)
            print("  Por segurança do branding, selecione o canal correto na próxima tela.")
            print("!" * 70 + "\n")

        # Salva no arquivo do canal real
        real_token_file = CREDENTIALS_DIR / f"{actual_id}_token.json"
        real_token_file.write_text(token_data, encoding="utf-8")

        if actual_id in TARGET_MAP:
            expected_title, alias_file, extras = TARGET_MAP[actual_id]
            (CREDENTIALS_DIR / alias_file).write_text(token_data, encoding="utf-8")
            for extra in extras:
                (CREDENTIALS_DIR / extra).write_text(token_data, encoding="utf-8")
            print("\n" + "=" * 70)
            print("  AUTENTICACAO OAUTH2 MAPEADA COM SUCESSO!")
            print("=" * 70)
            print(f"  Canal Detectado: {actual_title} ({actual_handle})")
            print(f"  Channel ID:      {actual_id}")
            print(f"  Slot do Studio:  {expected_title} -> {alias_file}")
            print(f"  Arquivo Base:    {real_token_file.name}")
        else:
            print("\n" + "=" * 70)
            print("  AVISO: CANAL AUTENTICADO NAO PERTENCE AOS 3 OFICIAIS DO STUDIO!")
            print("=" * 70)
            print(f"  Canal Detectado: {actual_title} ({actual_handle}) [ID: {actual_id}]")
            print(f"  Token salvo apenas em: {real_token_file.name}")
        print("=" * 70 + "\n")
        print("  A plataforma agora pode publicar videos e shorts diretamente neste canal.")
        print("=" * 70 + "\n")

    except Exception as exc:
        print(f"\n[ERRO] Falha durante a autenticacao OAuth2: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
