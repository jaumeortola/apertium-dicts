#!/bin/bash
dir_scripts="scripts/"
dir_results="results/"
lt_dict="src/lexique-dicollecte-fr-v6.1.txt"
original_apertium_dict="/home/jaume/apertium/apertium-fra/apertium-fra.fra.metadix"

#rm -rf $dir_results
#mkdir $dir_results

lang=$1

perl $dir_scripts/generate-apertium.pl $lang adj $lt_dict $original_apertium_dict > $dir_results/$lang-adj.txt 2>$dir_results/$lang-adj-diff.txt
#perl $dir_scripts/gen-french-names.pl $lt_dict $original_apertium_dict > $dir_results/french-names.txt

echo "Resultats en: $dir_results"
