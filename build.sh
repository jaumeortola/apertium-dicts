#!/bin/bash
dir_scripts="scripts/"
dir_results="results/"

#rm -rf $dir_results
#mkdir $dir_results

lang=$1

if [[ $lang = "fra" ]]; then
	apertium_dict="/home/jaume/apertium/apertium-fra/apertium-fra.fra.metadix"
	src_dict="src/lexique-dicollecte-fr-v6.1.txt"
fi
if [[ $lang = "cat" ]]; then
	apertium_dict="/home/jaume/apertium/apertium-cat/apertium-cat.cat.dix"
	src_dict="/home/jaume/github/catalan-dict-tools/resultats/lt/diccionari.txt"
fi

if [[ $lang = "spa" ]]; then
	apertium_dict="/home/jaume/apertium/apertium-spa/apertium-spa.spa.dix"
	src_dict="src/spanish-dict.txt"
fi

if [[ $lang = "eng" ]]; then
    apertium_dict="/home/jaume/apertium/apertium-eng/apertium-eng.eng.dix"
    src_dict="src/english-dict.txt"
fi

if [[ $lang = "por" ]]; then
    apertium_dict="/home/jaume/apertium/apertium-por/apertium-por.por.dix"
    src_dict="src/portuguese-dict.txt"
fi

if [[ $lang = "ita" ]]; then
    apertium_dict="/home/jaume/apertium/apertium-ita/apertium-ita.ita.dix"
    src_dict="src/italian-dict.txt"
fi

echo $apertium_dict
echo $src_dict

for gramcat in adv adj noun; do 
	perl $dir_scripts/generate-apertium.pl $lang $gramcat $src_dict $apertium_dict > $dir_results/$lang-$gramcat.txt 2>$dir_results/$lang-$gramcat-diff.txt
done

# superlatius -íssim
if [[ $lang = "cat" ]]; then
    gramcat="adj"
    perl $dir_scripts/extract-cat-superlatius.pl $lang $gramcat $src_dict $apertium_dict > $dir_results/superlatius-$lang-$gramcat.txt 2>$dir_results/superlatius-$lang-$gramcat-diff.txt
fi


echo "Results in: $dir_results"
