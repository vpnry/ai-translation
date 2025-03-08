#!/bin/bash

mkdir -p zzz_html_output

# Run each command sequentially, Vipassakarama will list on the web by date modified
# Thus ordered them here accordingly



# Dvemātikāpāḷi
TRAN=3
python3 join_translations.py vinaya_dvematika_pali/dvematikapali_46_chunks.xml --translations "$TRAN"
python3 gen_tpo_html.py \
    --md-file vinaya_dvematika_pali/dvematikapali_46_chunks_"$TRAN"_translations.md \
    --output zzz_html_output/dvematikapali_pali_english.html \
    --translations "$TRAN" \
    --title "Dvemātikāpāḷi" \
    --template pnry_tpo_html_template.html


echo "All HTML files have been generated."
