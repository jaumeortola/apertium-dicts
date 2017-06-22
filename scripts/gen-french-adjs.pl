use strict;
use warnings;
use autodie;
use utf8;

binmode( STDOUT, ":utf8" );

my $input_dict=$ARGV[0];
my $apertium_dict = $ARGV[1]; # paradigmes Apertium

open( my $fh,  "<:encoding(UTF-8)", $apertium_dict );

my $in_rule = 0;
my @rules;
my %paradigm_names;
my $rule ="";
while (my $line = <$fh>) {
    chomp($line);
    if ($line =~ /<pardef n="(.*_adj)".*>/) {
        $rule = $1;
        $in_rule = 1;
        my $sufix = "";
        if ($rule =~ /\/(.*)__adj/) {
            $sufix = $1;
        }
        $paradigm_names{$rule} = $sufix;
    } elsif ($line =~ /<\/pardef>/) {
        $in_rule = 0;
    } elsif ($in_rule) {
        if ($line =~ /<e(.*?)>.*?<p>(.*?)(<\/l>|<l\/>).*<r>(.*?)(<.*>)<\/r><\/p><\/e>/) {
            my $direction = $1;
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
            #print "$rule $postag $afig $line\n";
            if ($direction =~ /^$/) {
                push (@rules, "$rule $postag $afig");
            }
        }
    }
}
close ($fh);

@rules = sort @rules;

my %rules_in_oneline;

my $line = "";
my $rule_name = "";
my $prev_rule_name = "-1";
for my $line_rule (@rules) {     
    if ($line_rule =~ /(.*) (.*) (.*)/) {
        $rule_name = $1; 
        my $postag = $2;
        my $afig = $3;
        #print "$prev_rule_name $rule_name $1 $2 $3\n";
        if ($rule_name !~ /^$prev_rule_name$/) {
            $rules_in_oneline{$prev_rule_name} = $line;
            # Comença nou adjectiu
            $line = "$postag <r>$afig";
        } else {
            $line = $line." $postag <r>$afig";
        }
        $prev_rule_name = $rule_name;
    }
}
$rules_in_oneline{$prev_rule_name} = $line;

#print "REGLES\n";
#for my $rule_name (keys %rules_in_oneline) {
#    print "$rule_name $rules_in_oneline{$rule_name}\n";
#}
#print "FI REGLES\n";

my @adjs_lt;
open($fh,  "<:encoding(UTF-8)", $input_dict );
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
             push (@adjs_lt, "$lemme $newtag $flexion");    #lemma tags wordform
             #print "$lemme $newtag $flexion\n";
         }
    }
}
close ($fh);
@adjs_lt = sort @adjs_lt;




my %apertium_dict;
my %apertium_dict_paradigm;
open($fh,  "<:encoding(UTF-8)", $apertium_dict );
while (my $line = <$fh>) {
    chomp($line);
    
    if ($line =~ /<e lm="(.*)".*>.*<i>(.*)<\/i><par n="(.*__adj)"\/><\/e>/) {
        my $lema=$1;
        my $paradigm_name=$3;
        my $arrel=$2;
        my $flexio_ap = $rules_in_oneline{$paradigm_name};
        $flexio_ap =~ s/<r>/$arrel/g;
        $apertium_dict{$lema} = $flexio_ap;
        $apertium_dict_paradigm{$lema} = $paradigm_name;
    }
}
close ($fh);



$line = "";
my $lema = "";
my $prevlema = "-1";
for my $line_adj (@adjs_lt) {     
    if ($line_adj =~ /(.*) (.*) (.*)/) {
        $lema = $1; 
        my $postag = $2;
        my $wordform = $3;
        #print "$lema $prevlema $line\n";
        if ($lema !~ /^$prevlema$/) {
            &check_adjective($line);
            # Comença nou adjectiu
            $line = "$lema $postag $wordform";
        } else {
            $line = $line." $postag $wordform";
        }
        $prevlema = $lema;
    }
}
&check_adjective($line); # the last one



sub check_adjective {
    if ($line =~ /^$/) {
        return;
    }
    my $line = $_[0];
    #print "line ***** $line\n";
    my $flexio_lt = "";
    my $lema = "";
    if ($line =~ /(.*?) (.*)$/) {
        $lema = $1;
        $flexio_lt = $2;
    }

    # generate only non existent words
    if (!exists $apertium_dict{$lema}) {
        for my $rule_name (sort keys %paradigm_names) {
            #print "NOM REGLA: $rule_name\n";
            my $terminacio = $paradigm_names{$rule_name};
            if ($lema =~ /^(.*)$terminacio$/) {
                my $arrel = $1;
                my $flexio_ap = $rules_in_oneline{$rule_name};
                $flexio_ap =~ s/<r>/$arrel/g;
                $flexio_lt =~ s/(AQA|AO0)/AQ0/g;
                #if ($lema =~ /testamentaire/) {
                #    print "***** $rule_name $lema $arrel $flexio_ap ** $flexio_lt\n";
                #}
                if ($flexio_ap =~ /^$flexio_lt$/) {
                    print "<e lm=\"$lema\"><i>$arrel</i><par n=\"$rule_name\"/></e>\n";
                    return;
                }
            }
        }
        print "<e lm=\"$lema\"><i>$lema</i><par n=\"??????????\"/></e>\n";
    }



}

