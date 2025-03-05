#!/bin/bash

mkdir -p zzz_html_output

# Run each command sequentially

python3 join_translations.py vinaya-sangaha-attha/Vinayasaṅgaha-aṭṭhakathā_70_chunks.xml --translation 4
python3 gen_tpo_html.py \
    --md-file vinaya-sangaha-attha/Vinayasaṅgaha-aṭṭhakathā_70_chunks_4_translations.md \
    --output zzz_html_output/vinayasangaha_attha_pali_english.html \
    --translations 4 \
    --title "Vinayasaṅgaha-Aṭṭhakathā" \
    --template pnry_tpo_html_template.html

python3 join_translations.py vinayalankara-tika-1-2/vinayalankara-tika-1-2_139_chunks.xml --translation 3
python3 gen_tpo_html.py \
    --md-file vinayalankara-tika-1-2/vinayalankara-tika-1-2_139_chunks_3_translations.md \
    --output zzz_html_output/vinayalankara_tika_pali_english.html \
    --translations 3 \
    --title "Vinayālaṅkāra-Ṭīkā" \
    --template pnry_tpo_html_template.html

python3 join_translations.py vinaya_dvematika_pali/Dvemātikāpāḷi_46_chunks.xml --translation 3
python3 gen_tpo_html.py \
    --md-file vinaya_dvematika_pali/Dvemātikāpāḷi_46_chunks_3_translations.md \
    --output zzz_html_output/dvematikapali_pali_english.html \
    --translations 3 \
    --title "Dvemātikāpāḷi" \
    --template pnry_tpo_html_template.html

python3 join_translations.py vinaya-khuddasikkha/khudadasikkha-pura-abhinava-tika_212_chunks.xml --translation 3
python3 gen_tpo_html.py \
    --md-file vinaya-khuddasikkha/khudadasikkha-pura-abhinava-tika_212_chunks_3_translations.md \
    --output zzz_html_output/khudadasikkha-pura-abhinava-tika-pali-english.html \
    --translations 3 \
    --title "Khuddasikkhā-Purāṇaṭīkā-Abhinavaṭīkā" \
    --template pnry_tpo_html_template.html

echo "All HTML files have been generated."
