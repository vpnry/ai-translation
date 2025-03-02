# AI/LLM Translation Assistant  

This tool helps with AI-assisted translation by:  

- **`token_chunk_run_1.py`** – Splitting text into smaller chunks for AI translation  
- **Numbering** each line or paragraph for easier reference  
- **`check_translate.py`** – Verifying and checking translation results
- etc... 

> ## ⚠ Warning  
>
> AI/LLM-generated translations **can be inaccurate or misleading**. They should only be used as **references** and not as authoritative translations.  
> 
> However, they can be useful for **keyword searching** in full-text searches. By identifying where a topic appears in the text, you can then refer back to the **original Pāli/text** for a more precise understanding. This can save time when locating the original Pāli text.  

---

# How to Use  

## 1. Preparing Markdown for AI Translation  

To preserve formatting (bold, italics, etc.), use **Markdown** as the input for AI translation.  

### Steps:  
1. **Create a new document** in [Google Docs](https://docs.google.com/).  
2. **Copy and paste the formatted text** (e.g., from [Kaṅkhāvitaraṇī-aṭṭhakathā](https://tipitakapali.org/book/vin04t.nrf)) into Google Docs using:  
   - **Windows/Linux:** `Ctrl + C` → `Ctrl + V`  
   - **Mac:** `Cmd + C` → `Cmd + V`  
3. In **Google Docs**, go to **File > Download > Markdown (.md)**.  
4. Rename the extension `.md` file into `.txt`, **open the `.md` file** in a text editor like **VS Code**.  
5. **Clean up the text:**  
   - Replace ` ¶ ` with a space.  
   - Normalize spacing.  
6. **Use regex** to format elements like **headings** (`#`, `##`, etc.).  

---

## 2. Chunking, Tokenizing & Numbering Lines  

LLM models have input limits, so large texts must be **split into smaller chunks**.  

### Setup:  
- Create a virtual environment and install `tiktoken`:  

```bash
python3 -m venv .venv   
source .venv/bin/activate

pip install tiktoken pyperclip google-genai bs4 lxml prompt_toolkit

```  

### Chunking the Text:  
LLMs have different input/output limits. Adjust chunk sizes when running `token_chunk_run_1.py`  accordingly.

Run the following command to split the text:  

```bash

# using default --max-tokens 8000
python3 token_chunk_run_1.py -f your_text_file.txt

# using --max-tokens 2000
python3 token_chunk_run_1.py -f your_text_file.txt --max-tokens 2000

# if you want to process all .txt files in a directory:
python3 token_chunk_run_1.py -d your_text_file_directory

```  

This will generate a few files (**do not** rename these files, they will be used in the next steps): 

- **`your_text_file_{number}_chunks.xml`** – Chunked text with line IDs  
- **`your_text_file_{number}_chunks_translated_1.xml`** – Where you paste translated text by AI 1 
- **`your_text_file_{number}_chunks_translated_2.xml`** – Where you paste translated text by AI 2 
- **`your_text_file_{number}_chunks_translated_3.xml`** – Where you paste translated text by AI 3 

By checking **line IDs**, you can verify if the AI skipped any lines.

### Auto copy chunks


```bash

python3 chunk_copier_run_2.py

``` 

Run the script and follow the prompts to:
1. Enter the system prompt file path
2. Specify the chunked file path
3. Define how many chunks to copy at once
4. Provide a website URL to open after copying (option


### Checking the Translation:  
After translation, check for missing lines using:  

```bash
python3 check_translate.py your_text_file_{number}_chunks.xml

```  

If any lines are missing, manually translate them and run the check again.  

**WARNING: LLMs often merge stanzas (but not limited to only stanzas) together (often merged by meanings), which can result in missing IDs. In such cases, I usually have to correct them manually.** Example stanzas:  

> ID958=‘‘Āpattidassanussāho, na kattabbo kudācanaṃ;  
> ID959=Passissāmi anāpatti-miti kayirātha mānasaṃ.
> 
> ID960=‘‘Passitvāpi ca āpattiṃ, avatvāva punappunaṃ;  
> ID961=Vīmaṃsitvātha viññūhi, saṃsanditvā ca taṃ vade.
  

## 3. Generating Bilingual Files  

To generate bilingual and trilingual files, run the following command:

```bash
python3 create_bilingual_md_run_3.py your_text_file_{number}_chunks.xml
```

It is highly recommended to produce trilingual translations, as this allows us to compare outputs from multiple Large Language Models (LLMs).

---

## 4. Translation Prompt  

Translate chunks sequentially using the **system prompt** below.  

See [prompt_Pali_English.md](./prompt_Pali_English.md)

And 

See [prompt_Sinhala_English.md](./prompt_Sinhala_English.md)


### Customization:  
- Change **Kaṅkhāvitaraṇī-aṭṭhakathā** to your specific text.  
- Or modify **source** and **target** languages (e.g., English → Vietnamese).  

- Tips: 

  **`Pāli → English → Other Language`** seems to be more accurate than **`Pāli → (directly to) Other Language`**.  

---

## 5. Recommended LLM Models  

### **1. Google AI Studio**  
🔗 [Google AI Studio](https://aistudio.google.com/app/prompts/new_chat)  

#### Recommended Settings:  
- **Model:** `gemini-2.0-pro-exp-02-05` (2M token limit)  
- **Temperature:** `1.0` (or `1.3` for more creativity)  
- **Output length:** `8192`  
- **Top P:** `0.8`  
- **Safety settings:** All set to **"Block none"**  

⚠ **Gemini may still block translations due to safety filters, even when disabled.**  

---

### **2. Grok3 (As of Feb 20, 2025)**  
🔗 [Grok-3](https://grok.com/)  

- **Better prompt adherence**  
- **(So far) never blocks translations due to safety reasons**  

---

### **3. Alternative AI Models**  

- **[Claude](https://claude.ai/chats)**  
- **[ChatGPT](https://chatgpt.com/)**  
- **Qwen2.5-Max, Deepseek...**  

For the latest **top-performing** models, check:  
🔗 **[LM Arena Leaderboard](https://lmarena.ai/?leaderboard)**  

