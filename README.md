# SubForge

**Local AI-powered subtitle translation with Ollama and TranslateGemma. Generate natural, context-aware subtitles while preserving timestamps — no external translation services required.**

---

# 🇧🇷 Português

## Sobre o projeto

**SubForge** é uma ferramenta de tradução de legendas que utiliza modelos de inteligência artificial executados localmente para traduzir arquivos `.srt` de maneira contextualizada.

Em vez de traduzir cada linha isoladamente, o SubForge envia grupos de legendas ao modelo, permitindo que a IA considere o contexto dos diálogos e produza traduções mais naturais e coerentes.

O projeto utiliza o [Ollama](https://ollama.com/) para executar localmente o modelo [TranslateGemma 12B](https://ollama.com/library/translategemma), sem depender de APIs pagas ou serviços externos de tradução.

O SubForge foi desenvolvido para funcionar com diferentes filmes, séries e conteúdos legendados. Os idiomas de origem e destino podem ser configurados diretamente no script.

## Funcionalidades

- **Tradução contextual:** processa várias legendas em conjunto para preservar o contexto dos diálogos.
- **Idiomas configuráveis:** permite definir os idiomas de origem e destino.
- **Execução local:** utiliza o Ollama para executar o modelo de IA na própria máquina.
- **Preservação da sincronização:** mantém os índices e timestamps originais do arquivo SRT.
- **Preservação da formatação:** busca manter tags de formatação, como `<i>` e `</i>`.
- **Processamento em lotes:** divide a legenda em grupos menores para facilitar a tradução.
- **Contexto entre lotes:** utiliza falas anteriores como referência para melhorar a continuidade.
- **Checkpoint e retomada:** salva o progresso e permite continuar uma tradução interrompida.
- **Validação automática:** verifica a estrutura das respostas antes de salvar os resultados.

## Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Implementação do script |
| Ollama | Execução local do modelo |
| TranslateGemma 12B | Tradução das legendas |
| pysrt | Leitura e escrita de arquivos SRT |
| Requests | Comunicação com a API local do Ollama |
| tqdm | Barra de progresso |
| FFmpeg | Incorporação das legendas ao vídeo |

## Como funciona

O fluxo de tradução pode ser dividido em cinco etapas:

1. **Leitura:** o Python carrega o arquivo SRT original.
2. **Divisão:** as legendas são separadas em lotes de 20 entradas.
3. **Contextualização:** até 6 legendas anteriores são fornecidas como contexto para o próximo lote.
4. **Tradução:** o TranslateGemma processa o conteúdo e retorna as legendas traduzidas.
5. **Validação e salvamento:** o script verifica os índices e salva o progresso em um arquivo de checkpoint.

As legendas anteriores utilizadas como contexto não são traduzidas novamente. Elas servem apenas como referência para manter a coerência entre os lotes.

## Requisitos

- Linux, Windows ou macOS.
- Python 3.10 ou superior.
- [Ollama](https://ollama.com/).
- Memória RAM e/ou VRAM suficientes para executar o modelo TranslateGemma 12B.
- FFmpeg (opcional, caso queira incorporar as legendas diretamente ao vídeo).

> **Observação:** o desempenho e o consumo de memória dependem do hardware disponível. O modelo pode utilizar CPU e GPU conforme a configuração do Ollama.

## Instalação

### 1. Instale o Ollama

No Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Inicie o serviço:

```bash
sudo systemctl enable --now ollama
```

### 2. Baixe o modelo

```bash
ollama pull translategemma:12b
```

Para verificar se o modelo está funcionando:

```bash
ollama run translategemma:12b
```

### 3. Clone o repositório

```bash
git clone https://github.com/erastodib/SubForge.git
cd SubForge
```

### 4. Crie um ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows:

```powershell
.venv\Scripts\activate
```

### 5. Instale as dependências

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` contém as dependências Python necessárias:

```text
pysrt
requests
tqdm
```

O Ollama e o FFmpeg são ferramentas externas e devem ser instalados separadamente. Eles não fazem parte das dependências Python do projeto.

## Configuração

Antes de executar o programa, configure os parâmetros no início do script `translate_srt_ollama.py`.

Exemplo:

```python
MODEL = "translategemma:12b"

SOURCE_LANGUAGE = "English"
TARGET_LANGUAGE = "Brazilian Portuguese"

INPUT_FILE = "legenda_original.srt"
OUTPUT_FILE = "legenda_traduzida.srt"

CHECKPOINT_FILE = "translation_checkpoint.json"

BATCH_SIZE = 20
CONTEXT_SIZE = 6
MAX_RETRIES = 3
```

| Parâmetro | Descrição |
|---|---|
| `MODEL` | Modelo utilizado pelo Ollama |
| `SOURCE_LANGUAGE` | Idioma das legendas de entrada |
| `TARGET_LANGUAGE` | Idioma desejado para a tradução |
| `INPUT_FILE` | Caminho do arquivo SRT original |
| `OUTPUT_FILE` | Caminho da legenda traduzida |
| `CHECKPOINT_FILE` | Arquivo utilizado para salvar o progresso |
| `BATCH_SIZE` | Quantidade de legendas por lote |
| `CONTEXT_SIZE` | Quantidade de legendas anteriores utilizadas como contexto |
| `MAX_RETRIES` | Número máximo de tentativas em caso de falha |

Os idiomas podem ser alterados conforme a necessidade. Por exemplo:

```python
SOURCE_LANGUAGE = "Italian"
TARGET_LANGUAGE = "English"
```

Nesse caso, o programa tentará traduzir diretamente legendas em italiano para inglês.

> **Importante:** `SOURCE_LANGUAGE` deve corresponder ao idioma real do arquivo SRT de entrada. O idioma original do filme não é necessariamente o idioma das legendas utilizadas como entrada.

O script utiliza a API local do Ollama, normalmente disponível em:

```text
http://localhost:11434/api/generate
```

## Executando

Com o ambiente virtual ativado, o Ollama em execução e o modelo baixado:

```bash
python translate_srt_ollama.py
```

O progresso será exibido no terminal. Ao final, o arquivo traduzido será salvo no caminho definido em `OUTPUT_FILE`.

Se o processamento for interrompido, execute o script novamente para continuar utilizando o checkpoint existente.

> Caso altere o arquivo de entrada ou os parâmetros da tradução, remova o checkpoint antigo para evitar reutilizar resultados de uma execução anterior.

## Incorporando as legendas ao vídeo

O SubForge gera um arquivo SRT independente. Para incorporar permanentemente as legendas ao vídeo (*hard subtitles*), utilize o FFmpeg:

```bash
ffmpeg -i filme.mp4 \
-vf subtitles=legenda_traduzida.srt \
-c:a copy \
filme_legendado.mp4
```

Esse processo renderiza as legendas diretamente nos quadros do vídeo. O áudio é copiado sem recodificação.

## Privacidade e execução local

Toda a tradução é realizada localmente por meio do Ollama. O conteúdo das legendas é enviado apenas ao serviço local do modelo, sem necessidade de utilizar APIs externas de tradução.

O download inicial do modelo exige conexão com a internet, mas a tradução pode ser executada posteriormente sem conexão, desde que o modelo já esteja disponível na máquina.

# 🇺🇸 English

## About

**SubForge** is a subtitle translation tool that uses locally running artificial intelligence models to translate `.srt` files with contextual awareness.

Instead of translating each subtitle independently, SubForge processes groups of subtitles together, allowing the AI model to consider dialogue context and generate more natural and coherent translations.

The project uses [Ollama](https://ollama.com/) to run [TranslateGemma 12B](https://ollama.com/library/translategemma) locally, without relying on paid APIs or external translation services.

SubForge is designed to work with different movies, TV shows, and subtitled content. Source and target languages can be configured directly in the script.

## Features

- **Context-aware translation:** processes multiple subtitles together to preserve dialogue context.
- **Configurable languages:** allows users to define source and target languages.
- **Local execution:** runs the AI model directly on the user's machine through Ollama.
- **Timestamp preservation:** retains the original SRT indices and timestamps.
- **Formatting preservation:** attempts to preserve formatting tags such as `<i>` and `</i>`.
- **Batch processing:** splits subtitles into smaller groups for translation.
- **Cross-batch context:** uses previous subtitles as context to improve continuity.
- **Checkpoint and recovery:** saves progress and allows interrupted translations to resume.
- **Automatic validation:** checks the structure of model responses before saving the results.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Script implementation |
| Ollama | Local model execution |
| TranslateGemma 12B | Subtitle translation |
| pysrt | SRT file reading and writing |
| Requests | Communication with Ollama's local API |
| tqdm | Progress bar |
| FFmpeg | Hardcoding subtitles into video |

## How it works

The translation workflow consists of five main steps:

1. **Reading:** Python loads the original SRT file.
2. **Batching:** subtitles are divided into batches of 20 entries.
3. **Context:** up to 6 previous subtitles are provided as context for the next batch.
4. **Translation:** TranslateGemma processes the content and returns the translated subtitles.
5. **Validation and saving:** the script validates subtitle indices and saves progress to a checkpoint file.

Previous subtitles used as context are not translated again. They are only provided as references to maintain consistency between batches.

## Requirements

- Linux, Windows, or macOS.
- Python 3.10 or newer.
- [Ollama](https://ollama.com/).
- Sufficient RAM and/or VRAM to run TranslateGemma 12B.
- FFmpeg (optional, if you want to permanently embed subtitles into a video).

> **Note:** performance and memory usage depend on the available hardware. The model can use CPU and GPU resources according to the Ollama configuration.

## Installation

### 1. Install Ollama

On Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Start the service:

```bash
sudo systemctl enable --now ollama
```

### 2. Download the model

```bash
ollama pull translategemma:12b
```

To verify that the model is working:

```bash
ollama run translategemma:12b
```

### 3. Clone the repository

```bash
git clone https://github.com/erastodib/SubForge.git
cd SubForge
```

### 4. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 5. Install dependencies

With the virtual environment activated, run:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains the Python dependencies required by the project:

```text
pysrt
requests
tqdm
```

Ollama and FFmpeg are external tools and must be installed separately. They are not included in the project's Python dependencies.

## Configuration

Before running the program, configure the parameters at the beginning of `translate_srt_ollama.py`.

Example:

```python
MODEL = "translategemma:12b"

SOURCE_LANGUAGE = "English"
TARGET_LANGUAGE = "Brazilian Portuguese"

INPUT_FILE = "original_subtitles.srt"
OUTPUT_FILE = "translated_subtitles.srt"

CHECKPOINT_FILE = "translation_checkpoint.json"

BATCH_SIZE = 20
CONTEXT_SIZE = 6
MAX_RETRIES = 3
```

| Parameter | Description |
|---|---|
| `MODEL` | Ollama model used for translation |
| `SOURCE_LANGUAGE` | Language of the input subtitles |
| `TARGET_LANGUAGE` | Desired translation language |
| `INPUT_FILE` | Path to the original SRT file |
| `OUTPUT_FILE` | Path to the translated subtitle file |
| `CHECKPOINT_FILE` | File used to save translation progress |
| `BATCH_SIZE` | Number of subtitles per batch |
| `CONTEXT_SIZE` | Number of previous subtitles used as context |
| `MAX_RETRIES` | Maximum number of retry attempts after a failure |

Languages can be changed as needed. For example:

```python
SOURCE_LANGUAGE = "Italian"
TARGET_LANGUAGE = "English"
```

In this case, the program will attempt to translate Italian subtitles directly into English.

> **Important:** `SOURCE_LANGUAGE` must match the actual language of the input SRT file. The original language of the movie is not necessarily the language of the subtitles being translated.

The script communicates with Ollama through its local API, usually available at:

```text
http://localhost:11434/api/generate
```

## Running

With the virtual environment activated, Ollama running, and the model downloaded:

```bash
python translate_srt_ollama.py
```

Translation progress will be displayed in the terminal. Once completed, the translated SRT file will be saved to the path specified in `OUTPUT_FILE`.

If the process is interrupted, run the script again to resume using the existing checkpoint.

> If you change the input file or translation parameters, delete the previous checkpoint to avoid reusing results from an earlier run.

## Embedding subtitles into a video

SubForge generates a standalone SRT file. To permanently embed subtitles into a video (*hard subtitles*), use FFmpeg:

```bash
ffmpeg -i movie.mp4 \
-vf subtitles=translated_subtitles.srt \
-c:a copy \
subtitled_movie.mp4
```

This process renders the subtitles directly into the video frames. The audio stream is copied without re-encoding.

## Privacy and local execution

All translation is performed locally through Ollama. Subtitle content is sent only to the local model service, with no need for external translation APIs.

An internet connection is required for the initial model download. However, once the model is available locally, translation can be performed offline.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
