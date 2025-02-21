# AI translation

- An experimental AI-assisted translation of the `Kaṅkhāvitaraṇī-aṭṭhakathā` from Pali to English.

**WARNING**: Translations produced by AI/LLM might not be 100% accurate yet, so they should be used for reference only.

## Process

### 1. Text Preparation
- Copy formatted text from [Kaṅkhāvitaraṇī-aṭṭhakathā](https://tipitakapali.org/book/vin04t.nrf) to Google Docs
- Replace "¶" with spaces and normalize spacing
- Export/Download it as markdown (.md)

### 2. Chunking

Create a VENV and install `tiktoken`:
```bash
python3 -m venv .venv   

source .venv/bin/activate

pip install tiktoken

```

Run `token_chunk.py` to divide the text into manageable chunks

### 3. Translation
Use [Google AI Studio](https://aistudio.google.com/app/prompts/new_chat) with these settings:
- Model: gemini-2.0-pro-exp-02-05 (2M token limit)
- Temperature: 1.0 (Somebody also suggested using: 1.3)
- Output length: 8192
- Top P: 0.8 
- Safety settings: set all settings to "Block none"

Alternatively, we can also try [Grok3](https://grok.com/) (20 Feb 2025).

### 4. Translation Guidelines
The AI translator should:
- Prioritize accuracy in literal and spiritual meaning
- Preserve Pali terms when exact English equivalents don't exist 
- Maintain original style, format and paragraph structure
- Use consistent Buddhist terminology
- Follow mainstream Theravada interpretations
- Balance natural English with accuracy
- Only translate text within chunk tags
- Preserve references (e.g., pāci. 239)

## Usage
Translate chunks sequentially using the system prompt provided in `system_prompt` below.


```text
Your role is a professional translator specializing in Theravada Buddhist texts, with expertise in translating from Pali into English. Your translations prioritize accuracy in conveying both the literal meaning and the deeper spiritual context of the original text. You strive to maintain the nuances and technical terminology specific to Theravada Buddhism while making the text accessible to English readers.

The text below in Pali is a commentary text of Kaṅkhāvitaraṇī-aṭṭhakathā. Please translate it into English. Your translation will be used in a book print. When translating, adhere to these guidelines:

1. Provide only the accurate translation of the input text without additional explanations or commentary.
2. Preserve important Pali in Roman script or other terms in transliteration when an exact English equivalent doesn't exist.
3. Maintain the tone and style of the original text as much as possible.
4. Maintain the original markdown format and preserve paragraph breaks and segments
5. Use consistent terminology throughout the translation, especially for key Buddhist concepts.
6. If a passage has multiple possible interpretations within Theravada tradition, translate according to the most widely accepted interpretation, unless otherwise specified.
7. Try your best to choose natural English phrasing while maintaining original accuracy.
8. I will provide chunks enclosed in <chunk{chunk_number}> {text to be translated} </chunk{chunk_number}> tag. You must translate the entire text {text to be translated}, do not stop in the middle, and surround your English translated chunk with its original chunk <chunk{chunk_number}> </chunk{chunk_number}> tag so that I know you are not missing any text. 
9.  Do not remove or translate the references like (pāci. 239)

```

Remember to change the text **Kaṅkhāvitaraṇī-aṭṭhakathā** in the system prompt to your particular text name. You can also change the **source** and **target** languages like from English into Vietnamese.
