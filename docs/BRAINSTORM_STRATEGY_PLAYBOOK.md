# 🧠 PLAYBOOK ESTRATÉGICO & BRAINSTORMS — Dark Studio AI Platform

Este documento consolida todas as descobertas empíricas, análises forenses de dados de audiência, regras algorítmicas do YouTube e decisões arquiteturais desenvolvidas no projeto. Use este arquivo como contexto mestre ao abrir uma nova sessão de chat.

---

## 1. 🎯 A Fórmula Viral "Jim Simons" (Engenharia Reversa de Sucesso)

### 1.1 O Caso Empírico
* **Vídeo Campeão:** `Vb-MMJJXuMc` (*LTCM: Quando 2 Prêmios Nobel Quebraram Wall Street*)
* **Resultados em 24h:** 1.248+ visualizações orgânicas, 35 curtidas, 9 novos inscritos diretos, retenção média de 82%.
* **Comparação com Vídeos Stalled (0 a 5 views):** Títulos abstratos e genéricos ("A Tampa Soldada", "O Poço Profundo", "Água Fervente") com apenas 4 tags genéricas tiveram zero impressões no Shorts Feed.

### 1.2 Os 6 Pilares Inegociáveis da Fórmula
1. **Âncora de Entidade Notória (Notorious Person/Brand):**
   * Sempre vincular a narrativa a uma pessoa, instituição ou evento histórico específico e controverso (ex: *Jim Simons, Ed Thorp, Robert Merton, Valery Legasov, Federal Reserve, KGB*).
   * O algoritmo semântico do YouTube indexa nomes próprios com clusters de busca pré-existentes de alta afinidade.
2. **Números Extremos & Métricas Concretas:**
   * Títulos devem obrigatoriamente incluir números brutos de alto impacto: *"US$ 100 Bilhões", "Alavancagem 100:1", "12 Parafusos", "48 Horas", "US$ 3.6 Bilhões", "3 Milissegundos"*.
3. **Gancho Verbal de Paradoxo & Risco Máximo (0–3s):**
   * A primeira frase falada pelo narrador deve quebrar o padrão mental do espectador com uma contradição impossível:
     * *Exemplo:* "Dois homens ganharam o Prêmio Nobel de Economia em 1997... e em 1998 quase faliram o sistema bancário ocidental."
4. **Calibração de Duração Ótima (45s–55s para Shorts):**
   * Vídeos `<25s` sofrem penalidade algorítmica por superficialidade e baixo tempo de exibição acumulado.
   * Vídeos `>58s` apresentam drop-off na conclusão.
   * Faixa de ouro: **45s a 55s** (aproximadamente 420 a 500 caracteres de texto falado a 155 WPM).
   * **Trava física:** Duração mínima estrita de $\ge 28.0\text{s}$.
5. **Matriz Rica de SEO (13 a 15 Tags de Cauda Longa):**
   * Nunca usar menos de 12 tags. Combinar tags de marca, tags de nicho, tags de entidade e termos de busca com volume comprovado.
6. **Cadência Espaçada ($\ge 90$ minutos entre uploads):**
   * O YouTube ativa throttles automáticos de anti-spam caso múltiplos vídeos sejam publicados na mesma hora no mesmo canal. O intervalo mínimo entre Shorts deve ser de **90 a 120 minutos**.

---

## 2. 🩺 Performance Doctor Pós-24 Horas (`backend/core/performance_doctor.py`)

### 2.1 O Problema do "Canal Congelado"
* Vídeos recém-lançados que não recebem engajamento nas primeiras 24 horas correm o risco de ter a distribuição interrompida permanentemente pelo algoritmo.
* Deletar o vídeo reinicia o histórico negativamente e desperdiça tokens/renderização.

### 2.2 Política de Retrabalho Automático
* **Gatilho de Auditoria:** O daemon executa uma varredura a cada 6 horas.
* **Critério de Seleção:** Vídeos com mais de 24 horas de vida e $\le 5$ visualizações.
* **Ação Corretiva ao Vivo via YouTube Data API:**
  1. Reescreve o título aplicando a fórmula de Entidade + Número Extremo.
  2. Expande a descrição com timestamps, sinopse investigativa e hashtags de alto volume.
  3. Substitui o array de tags por uma lista curada de 13–15 tags de busca de alta relevância.
  4. Registra a auditoria em `workspace/automation/rework_log.json`.

---

## 3. 📦 Content Buffer & Fila de Estoque (`workspace/buffer/`)

### 3.1 O Risco da Dependência Just-in-Time
* Se a síntese de voz (TTS) ou a renderização de vídeo atrasar por latência de rede ou carga de GPU/CPU no momento exato da janela de postagem, o slot de horário nobre é perdido.

### 3.2 Arquitetura de Buffer Desacoplado
* **Diretórios de Estágio:**
  * `workspace/buffer/ch1/` (Canal #1: A Via da Descoberta)
  * `workspace/buffer/ch2/` (Canal #2: Finanças Quânticas)
* **Limiar de Segurança:**
  * Manter continuamente no mínimo **$\ge 3$ Shorts** e **$\ge 1$ Documentário Longo** pré-renderizados, auditados e prontos para disparo imediato por canal.
* **Disparo Instantâneo:** Na chegada da janela de horário nobre, o agendador consome o item mais antigo da fila local e publica em $< 10$ segundos.
* **Gatilho de Reabastecimento:** Sempre que o estoque local cair abaixo do limiar, o worker autônomo aciona a esteira de produção para repor o inventário.

---

## 4. 🛡️ Governança Anti-Garbage & Regras Físicas

### 4.1 Trava do Sentinel (`AntiGarbageSentinelAgent`)
* **Inspeção por OpenCV:** Amostra 8 frames do vídeo e calcula a entropia da imagem superior (`background_visual_std >= 8.5`) para assegurar que não há telas pretas estáticas com apenas legendas.
* **Inspeção de Movimento (`motion_delta_mean >= 0.35`):** Garante efeito Ken Burns, zoom progressivo ou vídeos b-roll reais em todas as cenas.
* **Padrão de Áudio:** Normalização EBU R128 a **$-14\text{ LUFS}$** com ducking automático de trilha sonora a $-21\text{ dB}$.
* **Durações Mínimas:**
  * Shorts: $25\text{s} \le \text{duração} \le 61\text{s}$ (ideal $45\text{s}–55\text{s}$).
  * Documentários Longos: $\ge 300\text{s}$ (5 a 12 minutos), com estrutura de 5 capítulos temáticos e 24 cenas dinâmicas.
* **Declaração YouTube:** Obrigatório enviar `containsSyntheticMedia=True` em todos os uploads.

---

## 5. 🗺️ Arquitetura Operacional do Ambiente

| Recurso | Detalhes / Localização |
| :--- | :--- |
| **Workspace Principal** | `/home/eudespatricio/dark_studio_platform` |
| **Python Virtualenv** | `/home/eudespatricio/dark_studio_platform/.venv/bin/python` |
| **Sessão tmux 24/7** | `dark_studio` (Janela 0: FastAPI Porta 8000 \| Janela 1: `cadence_daemon`) |
| **Tokens OAuth2** | `workspace/credentials/UC8RJWr3b2pKtnU1wOhV_bDQ_token.json` (Canal 1)<br>`workspace/credentials/UCE6Ch6nhxI81Z6ILQIw23_Q_token.json` (Canal 2) |
| **Estados Diários** | `workspace/automation/daily_cadence_state.json` (Canal 1)<br>`workspace/automation/quant_cadence_state.json` (Canal 2) |
| **Comando de Status Rápido** | `/home/eudespatricio/dark_studio_platform/flash_cadence_worker.sh --status` |
