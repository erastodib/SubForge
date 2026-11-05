#!/usr/bin/env python3
import json
import re
import time
from pathlib import Path
from typing import List, Tuple

import pysrt
import requests
from tqdm import tqdm


# =========================
# CONFIGURAÇÕES
# =========================

MODEL = "translategemma:12b"

INPUT_FILE = "[English] The Last Snows of Spring (1973) HD 1080p Full Movie [ENG SUB] [DownSub.com].srt"
OUTPUT_FILE = "The Last Snows of Spring.pt.ollama.srt"
CHECKPOINT_FILE = "translation_checkpoint.json"

OLLAMA_URL = "http://localhost:11434/api/generate"

SOURCE_LANGUAGE = "English"
TARGET_LANGUAGE = "Brazilian Portuguese"

# 20 costuma dar bom equilíbrio entre contexto e estabilidade.
# Se o modelo começar a quebrar estrutura, reduza para 10 ou 12.
BATCH_SIZE = 20

# Quantas legendas anteriores mandar só como contexto.
# Elas NÃO serão retraduzidas, apenas ajudam o modelo a entender a cena.
CONTEXT_SIZE = 6

MAX_RETRIES = 3


# =========================
# FUNÇÕES
# =========================

def block_to_text(sub: pysrt.SubRipItem) -> str:
    return f"{sub.index}\n{sub.start} --> {sub.end}\n{sub.text.strip()}"


def parse_srt_blocks(text: str) -> List[Tuple[int, str]]:
    """
    Retorna lista de (número_da_legenda, texto_traduzido).
    Ignora timestamps na hora de salvar, porque usamos os timestamps originais.
    """
    text = text.strip()

    # Remove code fences caso o modelo invente markdown
    text = re.sub(r"^```(?:srt)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # Divide por blocos começando com número
    pattern = re.compile(
        r"(?ms)^\s*(\d+)\s*\n"
        r"(?:\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}\s*\n)?"
        r"(.*?)(?=^\s*\d+\s*$|\Z)"
    )

    blocks = []
    for match in pattern.finditer(text):
        num = int(match.group(1))
        body = match.group(2).strip()
        blocks.append((num, body))

    return blocks


def make_prompt(context_blocks: List[pysrt.SubRipItem], target_blocks: List[pysrt.SubRipItem]) -> str:
    context_text = "\n\n".join(block_to_text(s) for s in context_blocks).strip()
    target_text = "\n\n".join(block_to_text(s) for s in target_blocks).strip()

    return f"""You are a professional subtitle translator.

Translate the TARGET subtitles from {SOURCE_LANGUAGE} into natural {TARGET_LANGUAGE}.

Prioritize fluent, natural dialogue over literal translations. Preserve the original meaning, tone, intent, and character voice. Use the surrounding context to understand ambiguous expressions, references, humor, and conversational nuances.

STRICT RULES:
- Return ONLY the translated TARGET subtitles.
- Preserve the exact subtitle numbers from the TARGET section.
- Preserve the exact timestamps from the TARGET section.
- Do not add explanations, comments, markdown, alternatives, or notes.
- Do not merge, split, remove, or add subtitle blocks.
- Preserve HTML tags such as <i> and </i>.
- Keep proper names unchanged unless they have an established localized form.
- Use natural language appropriate for the target audience, not literal machine translation.
- Keep lines concise and suitable for subtitles.

CONTEXT ONLY - do not translate these in the output:
{context_text if context_text else "(no previous context)"}

TARGET - translate only these subtitles:
{target_text}
"""


def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_ctx": 8192,
        },
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=600)
    response.raise_for_status()
    return response.json()["response"]


def load_checkpoint() -> dict:
    path = Path(CHECKPOINT_FILE)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_checkpoint(data: dict) -> None:
    Path(CHECKPOINT_FILE).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def main():
    input_path = Path(INPUT_FILE)

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {INPUT_FILE}")

    subs = pysrt.open(str(input_path), encoding="utf-8")
    checkpoint = load_checkpoint()

    total_batches = (len(subs) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"Modelo: {MODEL}")
    print(f"Entrada: {INPUT_FILE}")
    print(f"Saída: {OUTPUT_FILE}")
    print(f"Legendas: {len(subs)}")
    print(f"Lotes: {total_batches}")
    print()

    for start in tqdm(range(0, len(subs), BATCH_SIZE), desc="Traduzindo"):
        end = min(start + BATCH_SIZE, len(subs))
        batch_key = f"{start}-{end}"

        if batch_key in checkpoint:
            translated_map = checkpoint[batch_key]
            for idx in range(start, end):
                sub_number = str(subs[idx].index)
                if sub_number in translated_map:
                    subs[idx].text = translated_map[sub_number]
            continue

        context_start = max(0, start - CONTEXT_SIZE)
        context_blocks = subs[context_start:start]
        target_blocks = subs[start:end]

        expected_numbers = [s.index for s in target_blocks]

        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            prompt = make_prompt(context_blocks, target_blocks)

            try:
                raw = call_ollama(prompt)
                parsed = parse_srt_blocks(raw)

                parsed_numbers = [num for num, _ in parsed]

                if parsed_numbers != expected_numbers:
                    raise ValueError(
                        "Estrutura diferente do esperado.\n"
                        f"Esperado: {expected_numbers}\n"
                        f"Recebido: {parsed_numbers}\n"
                        f"Resposta bruta:\n{raw[:2000]}"
                    )

                translated_map = {str(num): text for num, text in parsed}

                for sub in target_blocks:
                    sub.text = translated_map[str(sub.index)]

                checkpoint[batch_key] = translated_map
                save_checkpoint(checkpoint)

                # salva parcial a cada lote
                subs.save(OUTPUT_FILE, encoding="utf-8")
                break

            except Exception as e:
                last_error = e
                print()
                print(f"Erro no lote {batch_key}, tentativa {attempt}/{MAX_RETRIES}:")
                print(e)
                time.sleep(2)

        else:
            print()
            print("Falhei nesse lote depois de várias tentativas.")
            print("Sugestão: reduza BATCH_SIZE para 10 e rode de novo.")
            raise last_error

    subs.save(OUTPUT_FILE, encoding="utf-8")

    print()
    print("Concluído!")
    print(f"Legenda salva em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
