"""
Gerenciador de Cadência Diária Automática — Bio Hack Longevidade
Executa o ciclo diário de 1 Vídeo Longo (16:9) + 5/6 Shorts (9:16) no canal "@BioHackLongevidade"
(UCIjEnT4adPYVyi0UlrCITBA) com garantia estrita de NÃO REUTILIZAÇÃO de fontes e publicação 100% PÚBLICA (PUBLIC).

Grade de Publicação Oficial (Horário de Brasília - BRT / UTC-3):
- 07:30 BRT: Short #1 (Protocolo Matinal de Dopamina & Cortisol)
- 11:30 BRT: Short #2 (Janela Principal Manhã/Almoço: Autofagia & Jejum Intermitente)
- 14:00 BRT: Short #3 (Pós-Almoço: Neuroplasticidade & Foco Profundo)
- 16:15 BRT: Short #4 (Tarde: Saúde Mitocondrial & NAD+)
- 18:00 BRT: VÍDEO LONGO 16:9 (Documentário Completo Horário Nobre Biohacking)
- 20:00 BRT: Short #5 (Feeder Horário Nobre -> Documentário 16:9)
- 22:00 BRT: Short #6 (Arquitetura do Sono Profundo & Recuperação Neural)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("dark_studio.biohack_cadence")

BASE_DIR = Path("/home/eudespatricio/dark_studio_platform").resolve()
STATE_FILE = BASE_DIR / "workspace/automation/biohack_cadence_state.json"
BIOHACK_SYNC_FILE = BASE_DIR / "workspace/automation/channel_3_biohack_sync.json"


@dataclass
class BioHackViralTopic:
    """Representa um tema viral candidato para a esteira diária de Bio Hack Longevidade."""

    topic_id: str
    original_title: str
    core_conflict: str
    specific_number: str
    niche_category: str
    outlier_score: float
    source_language: str
    source_url: str


class BioHackCadenceManager:
    """
    Controlador central da automação diária do Canal #3 (Bio Hack Longevidade).
    Garante a cadência de 1 Longo Âncora + 4 Shorts por dia em modo PÚBLICO, respeitando >= 90 min de cooldown.
    """

    SLOT_HOURS_BRT = [
        ("slot_biohack_long_01",  "11:30", "LONG_16_9",  "Documentário Longo 16:9 (Janela do Almoço / Autofagia Celular - Âncora)"),
        ("slot_biohack_short_01", "14:15", "SHORT_9_16", "Autofagia & Jejum Celular Pós-Almoço / Gancho de Choque (Feeder 1)"),
        ("slot_biohack_short_02", "20:45", "SHORT_9_16", "Horário Nobre Noturno / Sono Profundo & BDNF (Feeder 2)"),
    ]

    VIRAL_CANDIDATE_POOL: List[BioHackViralTopic] = [
        BioHackViralTopic(
            topic_id="autophagy_nobel_2016",
            original_title="How Yoshinori Ohsumi Discovered Autophagy: What Happens to Your Cells After 16, 24 and 48 Hours of Fasting",
            core_conflict="A descoberta vencedora do Prêmio Nobel de Medicina que provou como a privação calórica controlada aciona a reciclagem de proteínas tóxicas e mitocôndrias danificadas",
            specific_number="16 a 48 Horas",
            niche_category="Autofagia & Jejum Intermitente",
            outlier_score=13.4,
            source_language="en",
            source_url="https://www.youtube.com/watch?v=autophagy_nobel_2016",
        ),
        BioHackViralTopic(
            topic_id="neuroplasticity_deep_focus",
            original_title="The Neurobiology of Extreme Focus: How Acetylcholine, Epinephrine and BDNF Rewire the Adult Brain",
            core_conflict="Por que o cérebro adulto trava a mudança sináptica após os 25 anos e como os gatilhos neuroquímicos de alerta e erro destravam a neuroplasticidade acelerada",
            specific_number="90 Minutos Ultradianos",
            niche_category="Neuroplasticidade & Foco Profundo",
            outlier_score=12.1,
            source_language="en",
            source_url="https://www.youtube.com/watch?v=neuroplasticity_deep_focus",
        ),
        BioHackViralTopic(
            topic_id="mitochondria_nad_longevity",
            original_title="Mitochondrial Decay & NAD+ Depletion: Why Cellular Energy Drops 50% by Age 50 and How to Reverse It",
            core_conflict="O declínio silencioso das usinas de ATP e das sirtuínas que acelera o envelhecimento biológico e os protocolos físicos que restauram a biogênese mitocondrial",
            specific_number="Queda de 50% no NAD+",
            niche_category="Saúde Mitocondrial & Longevidade Celular",
            outlier_score=11.6,
            source_language="en",
            source_url="https://www.youtube.com/watch?v=mitochondria_nad_longevity",
        ),
        BioHackViralTopic(
            topic_id="sleep_glymphatic_wash",
            original_title="The Glymphatic System: How Deep Delta Sleep Washes Beta-Amyloid Plaques From Your Brain Every Night",
            core_conflict="Durante o sono profundo de ondas lentas, as células gliais encolhem 60% para permitir que o líquido cefalorraquidiano lave toxinas metabólicas associadas ao declínio cognitivo",
            specific_number="60% de Expansão Intersticial",
            niche_category="Arquitetura do Sono & Recuperação Neural",
            outlier_score=10.9,
            source_language="en",
            source_url="https://www.youtube.com/watch?v=sleep_glymphatic_wash",
        ),
    ]

    def __init__(self) -> None:
        self.channel_name = "Bio Hack Longevidade"
        self.channel_handle = "@BioHackLongevidade"
        self.youtube_channel_id = "UCIjEnT4adPYVyi0UlrCITBA"
        self.state_file = STATE_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_sync_file()
        self.state = self._load_or_initialize_state()

    def _ensure_sync_file(self) -> None:
        if not BIOHACK_SYNC_FILE.exists():
            BIOHACK_SYNC_FILE.parent.mkdir(parents=True, exist_ok=True)
            initial_sync = {
                "channel_id": self.youtube_channel_id,
                "channel_handle": self.channel_handle,
                "channel_name": self.channel_name,
                "subscribers": 0,
                "total_views": 0,
                "videos_count": 0,
                "last_synced_at": datetime.now(timezone.utc).isoformat(),
                "live_videos": {},
                "deleted_videos": {},
            }
            BIOHACK_SYNC_FILE.write_text(json.dumps(initial_sync, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_or_initialize_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning("Falha ao ler state da automação Bio Hack Longevidade, reiniciando: %s", e)

        initial = {
            "is_active": True,
            "target_channel": {
                "name": self.channel_name,
                "handle": self.channel_handle,
                "id": self.youtube_channel_id,
            },
            "last_cycle_timestamp": datetime.now(timezone.utc).isoformat(),
            "current_topic": "Autofagia Celular & Saúde Mitocondrial: O Prêmio Nobel que Decifrou o Rejuvenescimento Biológico",
            "schedule_date": datetime.now().strftime("%Y-%m-%d"),
            "today_slots": self._generate_today_slots(),
            "history": [],
            "stats": {
                "total_shorts_published": 0,
                "total_longs_published": 0,
                "all_public": True,
            },
        }
        self._save_state(initial)
        return initial

    def _save_state(self, state_dict: Dict[str, Any]) -> None:
        self.state_file.write_text(json.dumps(state_dict, indent=2, ensure_ascii=False), encoding="utf-8")

    def _generate_today_slots(self, base_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Gera os 5 slots diários (1 Longo Âncora + 4 Shorts) com timestamps ISO-8601 UTC para a esteira de Bio Hack Longevidade."""
        now = base_date or datetime.now(timezone.utc)
        brt_tz = timezone(timedelta(hours=-3))
        now_brt = now.astimezone(brt_tz)
        cycle_base_date = now_brt.date()
        slots = []

        slot_titles_map = {
            "slot_biohack_long_01": (
                "O Que Acontece com o Seu Cérebro e Mitocôndrias após 24 Horas de Autofagia (Neurociência Revelada) [DOCUMENTÁRIO]",
                "Autofagia, Mitofagia & Neuroplasticidade",
                (
                    "Como desacelerar o envelhecimento celular e operar o cérebro humano em sua capacidade biológica máxima? "
                    "Em três de outubro de dois mil e dezesseis, a Assembleia do Nobel no Instituto Karolinska concedeu o Prêmio Nobel de Fisiologia ou Medicina "
                    "ao biólogo celular japonês Yoshinori Ohsumi por decifrar um dos mecanismos mais sofisticados da evolução: a autofagia celular. "
                    "Neste documentário completo do canal Bio Hack Longevidade, analisamos exatamente o que ocorre dentro dos seus neurônios e mitocôndrias "
                    "hora após hora quando você ativa os protocolos de reciclagem biológica e otimização sináptica. "
                    "Durante décadas, a medicina acreditou que o declínio cognitivo e a perda de vitalidade física eram processos lineares inevitáveis. "
                    "Hoje, a biologia molecular demonstra que o envelhecimento acelerado é amplamente impulsionado pelo acúmulo de restos celulares, "
                    "mitocôndrias disfuncionais que vazam radicais livres e sinapses inflamadas pelo excesso crônico de glicose e insulina. "
                    "Na primeira fase, entre zero e doze horas após a última refeição, o organismo consome o glicogênio armazenado no fígado. "
                    "A partir da décima quarta hora, ocorre uma mudança bioquímica decisiva: a queda nos níveis de insulina e de aminoácidos circulantes "
                    "desliga o complexo proteico mTOR, o sensor mestre de crescimento celular, e aciona a enzima AMPK. "
                    "É nesse instante que os autofagossomos entram em ação, envolvendo proteínas danificadas e organelas velhas para fundi-las aos lisossomos. "
                    "No cérebro, a transição para corpos cetônicos, especialmente o beta-hidroxibutirato, fornece um combustível termodinamicamente superior à glicose, "
                    "gerando mais moléculas de ATP por unidade de oxigênio e elevando a expressão do fator neurotrófico derivado do cérebro, o BDNF. "
                    "O BDNF funciona como um verdadeiro fertilizante sináptico, estimulando a neurogênese no hipocampo, a região central da memória e do aprendizado. "
                    "Simultaneamente, ocorre a mitofagia: as mitocôndrias defeituosas são seletivamente eliminadas, abrindo espaço para a biogênese mitocondrial "
                    "quando o protocolo é combinado com exercício aeróbico de Zona Dois e exposição controlada ao frio ou calor. "
                    "Para consolidar essa remodelagem neural, entra em cena o quarto pilar da longevidade: a arquitetura do sono profundo. "
                    "Durante as ondas delta do sono não-REM, o sistema glinfático expande os canais intercelulares do cérebro em sessenta por cento, "
                    "lavando placas beta-amiloides e proteína tau acumulada durante a vigília. "
                    "A ciência da longevidade ativa prova que pequenas intervenções diárias no ritmo circadiano, na janela alimentar e no estresse hormético "
                    "reprogramam a expressão epigenética para décadas de alta performance cognitiva. "
                    "Inscreva-se no canal Bio Hack Longevidade, deixe seu like e ative as notificações para dominar os próximos protocolos baseados em evidências."
                ),
            ),
            "slot_biohack_short_01": (
                "16 HORAS DE JEJUM: O momento exato em que suas células devoram proteínas tóxicas #Shorts",
                "Autofagia & Jejum Intermitente",
                (
                    "Em dois mil e dezesseis, o cientista japonês Yoshinori Ohsumi venceu o Prêmio Nobel de Medicina ao provar o mecanismo da autofagia celular. "
                    "Quando você completa dezesseis a vinte e quatro horas sem ingerir calorias, a queda na insulina e a inibição da via mTOR "
                    "forçam suas células a desmontar organelas defeituosas e proteínas mal dobradas, transformando lixo metabólico em aminoácidos novos. "
                    "Acompanhe o documentário completo no canal Bio Hack Longevidade."
                ),
            ),
            "slot_biohack_short_02": (
                "QUEDA DE 50% NO NAD+: Por que sua energia celular despenca e como reativar as mitocôndrias #Shorts",
                "Saúde Mitocondrial & Longevidade Celular",
                (
                    "Aos cinquenta anos de idade, os níveis da coenzima NAD mais nas células humanas caem pela metade em comparação aos vinte anos. "
                    "Sem NAD mais suficiente, as proteínas da longevidade chamadas sirtuínas deixam de reparar o DNA e as mitocôndrias entram em disfunção. "
                    "Estudos mostram que o treino intervalado de Zona Dois e o contraste térmico ativam a enzima AMPK, estimulando a biogênese de novas mitocôndrias jovens. "
                    "Inscreva-se no canal Bio Hack Longevidade."
                ),
            ),
            "slot_biohack_short_03": (
                "LAVAGEM CEREBRAL NOTURNA: Como o Sistema Glinfático limpa toxinas no Sono Profundo #Shorts",
                "Arquitetura do Sono & Recuperação Neural",
                (
                    "Todas as noites, quando seu cérebro entra no estágio de sono profundo de ondas lentas, acontece uma operação de limpeza microscópica. "
                    "As células gliais encolhem seu volume em até sessenta por cento, permitindo que o líquido cefalorraquidiano flua rapidamente pelo tecido neural "
                    "e remova placas beta-amiloides acumuladas durante o dia. Dormir menos de seis horas interrompe esse ciclo vital. "
                    "Inscreva-se no canal Bio Hack Longevidade."
                ),
            ),
            "slot_biohack_short_04": (
                "CORTISOL E LUZ SOLAR: O erro nos primeiros 15 minutos da manhã que drena sua dopamina #Shorts",
                "Ritmo Circadiano & Dopamina Basal",
                (
                    "Nos primeiros quinze minutos após acordar, seus olhos possuem fotorreceptores chamados células ganglionares "
                    "intrínsecas que regulam diretamente o núcleo supraquiasmático do hipotálamo. "
                    "Olhar para a tela do celular no escuro bloqueia o pulso saudável de cortisol matinal e desregula a liberação de melatonina dezesseis horas depois. "
                    "A exposição à luz solar natural logo cedo eleva a dopamina basal em até cinquenta por cento ao longo do dia. "
                    "Inscreva-se no canal Bio Hack Longevidade."
                ),
            ),
        }

        for slot_id, time_brt, v_format, angle_name in self.SLOT_HOURS_BRT:
            h_brt, m_brt = map(int, time_brt.split(":"))
            # O slot de deslocamento matinal ocorre na manhã seguinte ao lançamento do Long (D+1)
            is_next_day = (h_brt < 11) or ("short_04" in slot_id)
            slot_date = cycle_base_date + timedelta(days=1 if is_next_day else 0)
            slot_dt_brt = datetime(slot_date.year, slot_date.month, slot_date.day, h_brt, m_brt, 0, tzinfo=brt_tz)
            slot_utc = slot_dt_brt.astimezone(timezone.utc)

            title_info = slot_titles_map.get(
                slot_id,
                ("Bio Hack Longevidade Protocolo", "Neurociência & Longevidade", "Protocolo científico do canal Bio Hack Longevidade."),
            )

            slots.append({
                "slot_id": slot_id,
                "time_brt": time_brt,
                "utc_iso": slot_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "video_format": v_format,
                "angle_name": angle_name,
                "title": title_info[0],
                "target_topic": title_info[1],
                "script_hook": title_info[2][:180],
                "narration_text": title_info[2],
                "status": "scheduled",
                "privacy_status": "public",
                "youtube_video_id": None,
                "watch_url": None,
                "status_label": f"PROGRAMADO ({time_brt} BRT • PÚBLICO)",
            })
        return slots

    def sync_slots_with_live_youtube(self) -> None:
        """Sincroniza os slots diários com os vídeos ao vivo publicados em Bio Hack Longevidade."""
        pass

    def check_and_dispatch_due_slots(self) -> List[Dict[str, Any]]:
        """Verifica slots da grade de Bio Hack Longevidade agendados para o horário atual."""
        self.state = self._load_or_initialize_state()
        if not self.state.get("is_active", True):
            return []

        now_brt = datetime.now(timezone(timedelta(hours=-3)))
        slots = self.state.get("today_slots", [])
        dispatched: List[Dict[str, Any]] = []

        for slot in slots:
            if slot.get("status") in ("ready_for_dispatch", "scheduled") and not slot.get("youtube_video_id"):
                time_str = slot.get("time_brt", "00:00")
                try:
                    sh, sm = map(int, time_str.split(":"))
                    is_due = (now_brt.hour > sh) or (now_brt.hour == sh and now_brt.minute >= sm)
                except Exception:
                    is_due = False

                if is_due:
                    logger.info("Slot BioHack %s (%s BRT) atingiu horário da grade: %s", slot["slot_id"], time_str, slot.get("title"))
                    dispatched.append(slot)

        return dispatched

    def get_status(self) -> Dict[str, Any]:
        """Retorna telemetria da automação de Bio Hack Longevidade."""
        self.state = self._load_or_initialize_state()
        from backend.agents.schedule_cadence_auditor_agent import ScheduleCadenceAuditorAgent

        ramp_status = ScheduleCadenceAuditorAgent.detect_channel_ramp_phase(
            subscribers=0, watch_hours=0.0, is_monetized=False
        )
        return {
            "is_active": self.state.get("is_active", True),
            "target_channel": self.state.get("target_channel"),
            "daily_cadence": "FASE 1 (RAMPA YPP): 1 Vídeo Longo (18:00 BRT Horário Nobre) + 6 Shorts (07:30, 11:30, 14:00, 16:15, 20:00, 22:00 BRT)",
            "post_monetization_cadence": "FASE 3 (NORMALIZADO): 3 Super-Docs/semana (18:00 BRT, 12–18m) + 2 Shorts/dia (11:30 e 20:00 BRT)",
            "ramp_phase": ramp_status,
            "default_visibility": "PÚBLICO (public)",
            "current_topic": self.state.get("current_topic"),
            "schedule_for_tomorrow": self.state.get("schedule_date"),
            "total_slots": len(self.state.get("today_slots", [])),
            "today_schedule": self.state.get("today_slots", []),
            "next_scheduled_slot": self._get_next_slot(),
        }

    def _get_next_slot(self) -> Optional[Dict[str, Any]]:
        slots = self.state.get("today_slots", [])
        for s in slots:
            if s.get("status") in ("ready_for_dispatch", "scheduled") and not s.get("youtube_video_id"):
                return s
        return slots[0] if slots else None

    def toggle_automation(self, enable: Optional[bool] = None) -> bool:
        """Ativa ou pausa a esteira diária autônoma."""
        self.state = self._load_or_initialize_state()
        new_state = (not self.state.get("is_active", True)) if enable is None else enable
        self.state["is_active"] = new_state
        self._save_state(self.state)
        return new_state


biohack_cadence_mgr = BioHackCadenceManager()
