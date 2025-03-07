# AI/LLM Translation Assistant  

These scripts are primarily for my personal use, but I'm sharing them here as a backup and for anyone who might find them useful. Apologies for any messy code!

---

## 📂 Script Overview

- **`token_chunk.py`** – Splits text into smaller chunks for AI translation, adding **line numbers** for easier reference.
- **`chunk_copier.py`** – Utility to process and copy XML-style text chunks to the clipboard with a system prompt.
- **`check_translate.py`** – Verifies and checks translation results.
- **`join_translations.py`** – Merges multiple translations into a bilingual or trilingual file.
- **`translate_dir_gemini.py`** – Translates all files in a directory using the Gemini API.
- **etc...**

---

## ⚠ Important Notice

AI/LLM-generated translations **can be inaccurate or misleading**. They should be used as **reference only**, not as definitive translations.

However, they are useful for **keyword searching** in full-text searches. By identifying where a topic appears in the text, you can refer to the **original Pāli/text** for precise understanding, saving time in locating key passages.

---

## 🚀 How to Use

### 1️⃣ Preparing Markdown for AI Translation

To preserve formatting (bold, italics, etc.), use **Markdown** as input for AI translation.

#### Steps:

There are many ways to get you source files converted into `markdown` format files. One complicated way is:

1. **Create a document** in [Google Docs](https://docs.google.com/).
2. **Copy and paste** formatted text (e.g., from [Kaṅkhāvitaraṇī-aṭṭhakathā](https://tipitakapali.org/book/vin04t.nrf)) into Google Docs:
   - **Windows/Linux:** `Ctrl + C` → `Ctrl + V`
   - **Mac:** `Cmd + C` → `Cmd + V`
3. In **Google Docs**, go to **File > Download > Markdown (.md)**.
4. Rename the `.md` file extension to `.txt`, then open it in **VS Code** or another text editor.
5. **Clean up the text:**
   - Replace ` ¶ ` with a space.
   - Normalize spacing.
6. **Use regex** to format elements like **headings** (`#`, `##`, etc.).

---

### 2️⃣ Chunking and Translating

Since LLMs have input limits, large texts must be **split into smaller chunks**.

#### Setup:

1. **Create a virtual environment and install dependencies:**

```bash
python3 -m venv .venv   

source .venv/bin/activate

pip install tiktoken pyperclip google-genai bs4 lxml prompt_toolkit ratelimit pandoc pypandoc unidecode



```

#### Chunking the Text:
Adjust `--max-tokens` based on the LLM’s input limit.

```bash
# Using default --max-tokens 6000
python3 token_chunk.py -f your_text_file.txt

# Using --max-tokens 2000
python3 token_chunk.py -f your_text_file.txt --max-tokens 5000

# Process all .txt files in a directory
python3 token_chunk.py -d your_text_file_directory
```

This generates chunked files (**do not rename them**, they are needed for later steps):

- **`your_text_file_{number}_chunks.xml`** – Chunked text with line IDs
- **`your_text_file_{number}_chunks_translated_1.xml`** – AI 1 translation
- **`your_text_file_{number}_chunks_translated_2.xml`** – AI 2 translation
- **`your_text_file_{number}_chunks_translated_3.xml`** – AI 3 translation
- ...

By checking **line IDs**, you can verify if the AI skipped any lines.

#### Auto Copy Chunks:

If you are using LLMs via their Web UI, this script will save you a lot of time:

```bash
python3 chunk_copier.py
```

Follow the prompts to:
1. Enter the system prompt file path.
2. Specify the chunked file path.
3. Define the number of chunks to copy at once.
4. Optionally, provide a website URL to open after copying.

#### Checking Translations:
After translation, verify for missing lines:

```bash
python3 check_translate.py
```

If any lines are missing, manually translate them and run the check again.

**⚠ Note:** LLMs often merge stanzas or meaning-related lines together, which can result in missing IDs.

Manual correction is required in such cases, the `check_translate.py` may help to list out the missing IDs.

Example stanzas:

```plaintext
ID958=‘‘Āpattidassanussāho, na kattabbo kudācanaṃ;  
ID959=Passissāmi anāpatti-miti kayirātha mānasaṃ.  
ID960=‘‘Passitvāpi ca āpattiṃ, avatvāva punappunaṃ;  
ID961=Vīmaṃsitvātha viññūhi, saṃsanditvā ca taṃ vade.  
```

---

### 3️⃣ Generating Bilingual/Multilingual Files

To merge translations into bilingual/trilingual files, run:

```bash
python3 join_translation.py
```

Using multiple LLM outputs allows better comparison and verification.

---

### 4️⃣ Translation Prompts

Translate chunks sequentially using the **system prompts**:

- [prompt_Pali_English.md](./prompt_Pali_English.md) 
  
- [prompt_Sinhala_English.md](./prompt_Sinhala_English.md)

#### Customization:
- Change **Vinayasaṅgaha-aṭṭhakathā** to your specific text.
- Modify **source** and **target** languages as needed.
- **Tip:** Translating **Pāli → English → Other Language** is often more accurate than translating **Pāli → Other Language** directly.

---

## 🔥 Recommended LLM Models

### 1️⃣ Google AI Studio  
🔗 [Google AI Studio](https://aistudio.google.com/app/prompts/new_chat)

#### Recommended Settings:
- **Model:** `gemini-2.0-pro-exp-02-05` (2M token limit)
- **Temperature:** `1.0` (or `1.3` for creativity)
- **Output length:** `8192`
- **Top P:** `0.8`
- **Safety settings:** All set to **"Block none"**

⚠ **Gemini may still block translations due to safety filters, even when disabled.**

---

### 2️⃣ Grok3 (As of Feb 20, 2025)  
🔗 [Grok-3](https://grok.com/)

- **Better prompt adherence**
- **(So far) never blocks translations due to safety reasons**

---

### 3️⃣ Alternative AI Models

- **[Claude](https://claude.ai/chats)**
- **[ChatGPT](https://chatgpt.com/)**
- **Deepseek, etc.**

For the latest top-performing models, check:
🔗 **[LM Arena Leaderboard](https://lmarena.ai/?leaderboard)**

