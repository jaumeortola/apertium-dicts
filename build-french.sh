#!/bin/bash
dir_scripts="scripts/"
dir_results="results/"
lt_dict="src/lexique-dicollecte-fr-v6.1.txt"
original_apertium_dict="/home/jaume/apertium/apertium-fra/apertium-fra.fra.metadix"

rm -rf $dir_results
mkdir $dir_results

perl $dir_scripts/gen-french-adjs.pl $lt_dict $original_apertium_dict > $dir_results/french-adjs.txt
#perl $dir_scripts/gen-french-names.pl $lt_dict $original_apertium_dict > $dir_results/french-names.txt

echo "Resultats en: $dir_results"
