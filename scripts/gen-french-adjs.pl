use strict;
use warnings;
use autodie;
use utf8;

binmode( STDOUT, ":utf8" );

my $dict_entrada=$ARGV[0];
my $regles = $ARGV[1]; # paradigmes Apertium

open( my $fh,  "<:encoding(UTF-8)", $regles );

my $inregla = 0;
my @regles;
my %nomsregles;
my $spfx;
my $regla ="";
while (my $line = <$fh>) {
    chomp($line);
    if ($line =~ /<pardef n="(.*_adj)".*>/) {
		$regla = $1;
		#$spfx =$2;
		$inregla = 1;
		my $sufix = "";
		if ($regla =~ /\/(.*)__adj/) {
			$sufix = $1;
		}
		$nomsregles{$regla} = $sufix;
    } elsif ($line =~ /<\/pardef>/) {
		$inregla = 0;
    } elsif ($inregla) {
		if ($line =~ /<e(.*?)>.*?<p>(.*?)(<\/l>|<l\/>).*<r>(.*?)(<.*>)<\/r><\/p><\/e>/) {
		    my $etiquetes=$5;
		    my $lleva=$4;
		    my $afig=$2;
		    $afig =~ s/<l>(.*)/$1/;
		    my $nombre = "S";
		    if ($etiquetes =~ /"pl"/) { $nombre= "P";}
		    if ($etiquetes =~ /"sp"/) { $nombre= "N";}
		    my $genere = "M";
		    if ($etiquetes =~ /"mf"/) { $genere= "C";}
		    if ($etiquetes =~ /"f"/) { $genere= "F";}
		    my $categoria = "AQ0";
		    #if ($etiquetes =~ /"sup"/) { $categoria= "AQA";}
		    my $postag= $categoria.$genere.$nombre."0";
		    #print "$regla $postag $afig $line\n";
		    push (@regles, "$regla $postag $afig");
		}
    }
}
close ($fh);

@regles = sort @regles;

my %regles_unalinia;

my $linia = "";
my $nomregla = "";
my $prevnomregla = "-1";
for my $linia_regla (@regles) { 	
	if ($linia_regla =~ /(.*) (.*) (.*)/) {
		$nomregla = $1; 
		my $postag = $2;
		my $afig = $3;
		#print "$prevnomregla $nomregla $1 $2 $3\n";
		if ($nomregla !~ /^$prevnomregla$/) {
			$regles_unalinia{$prevnomregla} = $linia;
			# Comença nou adjectiu
			$linia = "$postag <r>$afig";
		} else {
			$linia = $linia." $postag <r>$afig";
		}
		$prevnomregla = $nomregla;
	}
}
$regles_unalinia{$prevnomregla} = $linia;

#print "REGLES\n";
#for my $nomregla (keys %regles_unalinia) {
#	print "$nomregla $regles_unalinia{$nomregla}\n";
#}
#print "FI REGLES\n";

my @adjectius_lt;
open($fh,  "<:encoding(UTF-8)", $dict_entrada );
while (my $line = <$fh>) {
    chomp($line);
    if ($line =~ /^\d+\t(.*?)\t(.*?)\t(.*?)\t.*/) { #Id Flexion Lemme Étiquettes
 		my $tags = $3;
 		my $flexion = $1;
 		my $lemme = $2;
 		my $genere = "C";
 		my $nombre = "N";
 		if ($tags =~ /\badj\b/) { 
 			if ($tags =~ /\bmas\b/) { $genere = "M"; } 
 			if ($tags =~ /\bfem\b/) { $genere = "F"; } 
 			if ($tags =~ /\bpl\b/) { $nombre = "P"; } 
 			if ($tags =~ /\bsg\b/) { $nombre = "S"; } 
 			my $newtag = "AQ0".$genere.$nombre."0";
 			push (@adjectius_lt, "$lemme $newtag $flexion");    #lemma tags wordform
 			#print "$lemme $newtag $flexion\n";
 		}
    }
}
close ($fh);
@adjectius_lt = sort @adjectius_lt;

$linia = "";
my $lema = "";
my $prevlema = "-1";
for my $linia_adj (@adjectius_lt) { 	
	if ($linia_adj =~ /(.*) (.*) (.*)/) {
		$lema = $1; 
		my $postag = $2;
		my $wordform = $3;
		#print "$lema $prevlema $linia\n";
		if ($lema !~ /^$prevlema$/) {
			&comprova_adjectiu($linia);
			# Comença nou adjectiu
			$linia = "$lema $postag $wordform";
		} else {
			$linia = $linia." $postag $wordform";
		}
		$prevlema = $lema;
	}
}
&comprova_adjectiu($linia);



sub comprova_adjectiu {
	if ($linia =~ /^$/) {
		return;
	}
    my $linia = $_[0];
    #print "LINIA ***** $linia\n";
    my $flexio_lt = "";
    my $lema = "";
    if ($linia =~ /(.*?) (.*)$/) {
    	$lema = $1;
    	$flexio_lt = $2;
    }
    for my $nomregla (sort keys %nomsregles) {
    	#print "NOM REGLA: $nomregla\n";
    	my $terminacio = $nomsregles{$nomregla};
    	if ($lema =~ /^(.*)$terminacio$/) {
    		my $arrel = $1;
    		my $flexio_ap = $regles_unalinia{$nomregla};
    		$flexio_ap =~ s/<r>/$arrel/g;
    		$flexio_lt =~ s/(AQA|AO0)/AQ0/g;
    		#if ($lema =~ /testamentaire/) {
    		#	print "***** $nomregla $lema $arrel $flexio_ap ** $flexio_lt\n";
    		#}
    		if ($flexio_ap =~ /^$flexio_lt$/) {
    			print "<e lm=\"$lema\">        <i>$arrel</i><par n=\"$nomregla\"/></e>\n";
    			return;
    		}
    	}
	}
	print "<e lm=\"$lema\">        <i>$lema</i><par n=\"??????????\"/></e>\n";
}

