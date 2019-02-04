python3 main.py < "plantilla-traduccions - traduccions.tsv" > output.txt
uniq cat.dix > cat2.dix
mv cat2.dix cat.dix
uniq spa.dix > spa2.dix
mv spa2.dix spa.dix
uniq spa-cat.dix > spa-cat2.dix
mv spa-cat2.dix spa-cat.dix
