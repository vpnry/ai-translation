#!/bin/bash

mkdir -p zzz_html_output

# Run each command sequentially, Vipassakarama will list on the web by date modified
# Thus ordered them here accordingly


# Vinayasaṅgaha-Aṭṭhakathā
TRAN=3
python3 join_translations.py vinaya_sangaha_attha/vinayasangaha-atthakatha_70_chunks.xml --translations "$TRAN"

python3 gen_tpo_html.py \
    --md-file vinaya_sangaha_attha/vinayasangaha-atthakatha_70_chunks_"$TRAN"_translations.md \
    --output zzz_html_output/vinayasangaha_attha_pali_english.html \
    --translations "$TRAN" \
    --title "Vinayasaṅgaha-Aṭṭhakathā" \
    --template pnry_tpo_html_template.html

# Vinayālaṅkāra-Ṭīkā
TRAN=3
python3 join_translations.py vinayalankara_tika_12/vinayalankara_tika_12_139_chunks.xml --translations "$TRAN"
python3 gen_tpo_html.py \
    --md-file vinayalankara_tika_12/vinayalankara_tika_12_139_chunks_"$TRAN"_translations.md \
    --output zzz_html_output/vinayalankara_tika_pali_english.html \
    --translations "$TRAN" \
    --title "Vinayālaṅkāra-Ṭīkā" \
    --template pnry_tpo_html_template.html

# Dvemātikāpāḷi
TRAN=2
python3 join_translations.py vinaya_dvematika_pali/dvematikapali_46_chunks.xml --translations "$TRAN"
python3 gen_tpo_html.py \
    --md-file vinaya_dvematika_pali/dvematikapali_46_chunks_"$TRAN"_translations.md \
    --output zzz_html_output/dvematikapali_pali_english.html \
    --translations "$TRAN" \
    --title "Dvemātikāpāḷi" \
    --template pnry_tpo_html_template.html


# Khuddasikkhā-Purāṇaṭīkā-Abhinavaṭīkā
TRAN=2
python3 join_translations.py vinaya_khuddasikkha/khudadasikkha-pura-abhinava-tika_212_chunks.xml --translations "$TRAN"
python3 gen_tpo_html.py \
    --md-file vinaya_khuddasikkha/khudadasikkha-pura-abhinava-tika_212_chunks_"$TRAN"_translations.md \
    --output zzz_html_output/khudadasikkha_pura_abhinava_tika_pali_english.html \
    --translations "$TRAN" \
    --title "Khuddasikkhā-Purāṇaṭīkā-Abhinavaṭīkā" \
    --template pnry_tpo_html_template.html



TRAN=2
python3 join_translations.py vinaya_sasanavataranaya/sasanavataranaya_60_chunks.xml --translations "$TRAN"

python3 gen_tpo_html.py \
    --md-file vinaya_sasanavataranaya/sasanavataranaya_60_chunks_"$TRAN"_translations.md \
    --output vinaya_sasanavataranaya/sasanavataranaya_sinh_english.html \
    --translations "$TRAN" \
    --title "Sāsanāvataraṇaya" \
    --template vinaya_sasanavataranaya/template.html

echo "All HTML files have been generated."
