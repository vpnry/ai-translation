# get latest code snippet from
# https://aistudio.google.com/prompts/new_chat
# in the top right corner, click Get code

import argparse
import time
from google import genai
from google.genai import types
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.validation import Validator, ValidationError

from chunk_copier import load_file_content, extract_chunks


key_file = "./gemini_key_project_2.txt"


# Gemini safety settings
# https://ai.google.dev/gemini-api/docs/safety-settings
gemini_safety = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_CIVIC_INTEGRITY",
        threshold="OFF",
    ),
]


def get_validated_input(message: str, validator=None, completer=None) -> str:
    """Get input with validation and completion"""
    try:
        return prompt(
            message,
            validator=validator,
            completer=completer,
            complete_while_typing=True,
        ).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled by user")
        exit(0)


class NumberValidator(Validator):
    def validate(self, document):
        text = document.text.strip()
        if text and not text.isdigit():
            raise ValidationError(message="Please enter a valid number")


def do_think(
    chunk_no: int,
    system_prompt: str,
    chunk_text: str,
    save_stream_file: str = "thought.xml",
):
    # output token can be upto 65,536,
    # so input (prompt + translating chunks) tokens can be around 40,000, but please use around 20,000
    # python3 token_chunk.py -f dvematikapali.txt --max-tokens 20000

    client = genai.Client(api_key=load_file_content(key_file).strip())
    model = "gemini-2.0-flash-thinking-exp-01-21"

    pc = chunk_text.strip()
    prompt_contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=pc),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.8,  # default 0.95
        top_k=64,
        max_output_tokens=65536,
        safety_settings=gemini_safety,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=system_prompt),
        ],
    )

    try:
        with open(save_stream_file, "a") as f:
            f.write(f"<think{chunk_no}>\n\n")
            f.flush()

            for chunk in client.models.generate_content_stream(
                model=model,
                contents=prompt_contents,
                config=generate_content_config,
            ):
                f.write(chunk.text)
                f.flush()
                print(chunk.text, end="")

            f.write(f"\n\n</think{chunk_no}>\n\n\n")
            f.flush()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print(f"\nStreaming output saved to: {save_stream_file}")
    return True


def gemini_think(
    chunk_file,
    save_stream_file,
    start_chunk=1,
    sys_prompt_file="./prompt_think_pali_eng.md",
):
    system_prompt = load_file_content(sys_prompt_file)
    system_prompt = system_prompt.strip()
    chunks = extract_chunks(load_file_content(chunk_file))

    for n, text in chunks:
        if n < start_chunk:
            print(f"Skipping chunk {n}")
            continue

        chunk_text = f"<chunk{n}>\n\n{text}\n\n</chunk{n}>"

        # limit 10 requests/minute
        print(f"\nThinking chunk {n}")

        do_think(
            chunk_no=n,
            system_prompt=system_prompt,
            chunk_text=chunk_text,
            save_stream_file=save_stream_file,
        )
        print(f"Done thinking chunk {n}. Will sleep for 30 seconds.")
        time.sleep(30)
    print("Done chunks are processed")


def main():
    parser = argparse.ArgumentParser(
        description="Process text chunks using Gemini API with CLI and interactive input."
    )
    parser.add_argument(
        "--chunk_file", type=str, help="Path to the chunk file (XML format)"
    )
    parser.add_argument(
        "--save_stream_file",
        type=str,
        help="Path to the file to save the Gemini output",
    )
    parser.add_argument(
        "--sys_prompt_file",
        type=str,
        default="./prompt_think_pali_eng.md",
        help="Path to the system prompt file",
    )

    args = parser.parse_args()

    # Use argparse values if provided, otherwise prompt user.
    chunk_file = (
        args.chunk_file
        if args.chunk_file
        else get_validated_input(
            "Enter the chunk file path: ", completer=PathCompleter()
        )
    )

    save_stream_file = (
        args.save_stream_file
        if args.save_stream_file
        else get_validated_input(
            "Enter the file path to save the Gemini output: ", completer=PathCompleter()
        )
    )

    sys_prompt_file = args.sys_prompt_file

    # Interactive loop for start chunk
    while True:
        start_chunk_input = get_validated_input(
            "Enter the chunk number to start from (or press Enter to start from the beginning): ",
            validator=None,  # Allow empty input and numbers
        )
        if start_chunk_input == "":
            start_chunk = 1
            break
        try:
            start_chunk = int(start_chunk_input)
            break
        except ValueError:
            print(
                "Invalid input. Please enter a number or press Enter to start from the beginning."
            )

    gemini_think(chunk_file, save_stream_file, start_chunk, sys_prompt_file)


if __name__ == "__main__":
    main()
