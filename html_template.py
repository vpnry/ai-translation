"""HTML template for Titpitakapali.org dictionary and TOC """


def generate_html_header(base_name: str) -> str:
    """Generate common HTML header"""
    return f"""<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{base_name}</title>
<style>
body {{font-size: medium; font-family: 'Noto Sans', 'DejaVu Sans', 'Times Ext Roman', 'Indic Times', 'Doulos SIL', Tahoma, 'Arial Unicode MS', Gentium;}}
.s1 {{text-align: left;border-left: 8px solid rgba(160, 82, 45, 0.5); padding-left: 5px;background:linear-gradient(to right, transparent, rgba(160, 82, 45, 0.3), transparent);}}
.t1 {{ text-align: justify;padding-left: 6px; border-left: 5px solid #ce93d8;border-radius: 10px; }}  /* Brown */.t2 {{ text-align: justify;padding-left: 6px; border-left: 5px solid rgba(70, 130, 180, 0.5);border-radius: 10px; }} /* Steel Blue */.t3 {{ text-align: justify;padding-left: 6px; border-left: 5px solid rgba(34, 139, 34, 0.5);border-radius: 10px; }}  /* Forest Green */.t4 {{ text-align: justify;padding-left: 6px; border-left: 5px solid rgba(255, 165, 0, 0.5);border-radius: 10px; }}  /* Orange */.t5 {{ text-align: justify;padding-left: 6px; border-left: 5px solid rgba(128, 0, 128, 0.5);border-radius: 10px; }}  /* Purple */.t6 {{ text-align: justify;padding-left: 6px; border-left: 5px solid rgba(255, 0, 0, 0.5);border-radius: 10px; }}    /* Red */.t7 {{ text-align: justify;padding-left: 6px; border-left: 5px solid rgba(0, 0, 255, 0.5);border-radius: 10px; }}    /* Blue */.t8 {{ text-align: justify;padding-left: 6px; border-left: 5px solid rgba(255, 20, 147, 0.5);border-radius: 10px; }} /* Deep Pink */.t9 {{ text-align: justify;padding-left: 6px; border-left: 5px solid rgba(0, 255, 255, 0.5);border-radius: 10px; }}  /* Cyan */.t10 {{ text-align: justify;padding-left: 6px; border-left: 5px solid rgba(255, 255, 0, 0.5); }} /* Yellow */
a {{text-decoration: none;}}
</style>
<link href="https://tipitakapali.org/web/tp.css" rel="stylesheet" />
<script src="https://tipitakapali.org/web/theme.js"></script>
</head>
<body>
<div id="dictionary-res"></div>
<p id="floatingTocButton"> 📜 </p>
<div id="tocDivBox" style="display: none;"></div>"""


def generate_title_section(base_name: str, num_translations: int) -> str:
    """Generate title section with translations info"""
    translations = "\n".join(
        [
            f'<p style="color: #444; font-size: 14px; margin: 8px 0;" class="t{i}">Translation {i}: <span style="color: #006400;">AI {i}</span> (DD MM YYYY)</p>'
            for i in range(1, num_translations + 1)
        ]
    )

    return f"""<div style="border: 2px solid #8B4513; border-radius: 8px; padding: 20px; background: linear-gradient(to bottom, #FFF8DC, #FAEBD7); box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 20px auto; max-width: 800px;">
<h2 style="color: #8B4513; text-align: center; margin-bottom: 15px; font-size: 28px;">{base_name}</h2>
<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">
<p style="color: #DC3545; font-weight: bold; text-align: center; font-size: 16px; margin: 15px 0;">WARNING: THIS IS AN AI-TRANSLATED EXPERIMENT.</p>
<p>Please do not blindly trust the LLM output. LLMs can produce errors. If you are uncertain, refer to the original Pāḷi text for verification.<br>
The main purpose of this page is to facilitate quick searches using English keywords to locate relevant Pāḷi passages.</p>
<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">
<p style="color: #444; font-size: 14px; margin: 8px 0;" class="s1">Source text: <a href="https://example.com" target="_blank">Your source text here</a> (DD MM YYYY)</p>
{translations}
<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">
</div>"""


def generate_html_footer() -> str:
    """Generate common HTML header"""
    return """<script defer="" src="https://tipitakapali.org/web/paliscriptconverter_edited.js"></script><script defer="" src="https://tipitakapali.org/web/handleClick.js"></script><script defer="" src="https://tipitakapali.org/web/renderer.js"></script>
</body></html>"""


if __name__ == "__main__":
    check_fix_unclosed_tag(
        "zzza/Vinayasaṅgaha-aṭṭhakathā_204_chunks_translated_4.xml",
        "zzza/Vinayasaṅgaha-aṭṭhakathā_204_chunks_translated_4.xml",
    )
