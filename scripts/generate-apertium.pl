use strict;
use warnings;
use autodie;
use utf8;

binmode( STDOUT, ":utf8" );
binmode( STDERR, ":utf8" );


my $lang = $ARGV[0]; #language (fra, cat, spa, eng...)
my $gram_cat = $ARGV[1]; #grammar category (adj, name)
my $input_dict = $ARGV[2]; # Other dictionary: Dicollecte, LanguageTool, etc.
my $apertium_dict = $ARGV[3]; # Apertium dictionary

my $apertium_gramcat = "";
my $dicollecte_gramcat = "";
my $lt_prev = "";
my $lt_post = "";
my $lt_tag_start;

if ($gram_cat =~ /^adj$/) {
    $apertium_gramcat = "adj";
    $dicollecte_gramcat = "adj";
    $lt_prev = "AQ0";
    $lt_post = "0";
    $lt_tag_start = "A";
} 
if ($gram_cat =~ /^name$/) {
    $apertium_gramcat = "n";
    $dicollecte_gramcat = "nom";
    $lt_prev = "NC";
    $lt_post = "000";
    $lt_tag_start = "NC";
} 


open( my $fh,  "<:encoding(UTF-8)", $apertium_dict );

my $global_errors = "";
my $global_errors2 = "";
my $global_errors3 = "";

my $in_rule = 0;
my @rules;
my %paradigm_names;
my $rule ="";
while (my $line = <$fh>) {
    chomp($line);
    if ($line =~ /<pardef n="(.*__$apertium_gramcat)".*>/) {
        $rule = $1;
        $in_rule = 1;
        my $sufix = "";
        if ($rule =~ /\/(.*)__$apertium_gramcat/) {
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
            #if ($etiquetes =~ /"sup"/) { $categoria= "AQA";}
            my $postag= $lt_prev.$genere.$nombre.$lt_post;
            #print "$rule $postag $afig $line\n";

            if ($lang !~ /^fra$/ || $direction =~ /^$/) {
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

if ($lang =~ /^fra$/) {
    while (my $line = <$fh>) {
        chomp($line);
        if ($line =~ /^\d+\t(.*?)\t(.*?)\t(.*?)\t.*/) { #Id Flexion Lemme Étiquettes
             my $tags = $3;
             my $flexion = $1;
             my $lemme = $2;
             my $genere = "C";
             my $nombre = "N";
             if ($tags =~ /\b$dicollecte_gramcat\b/) { 
                 if ($tags =~ /\bmas\b/) { $genere = "M"; } 
                 if ($tags =~ /\bfem\b/) { $genere = "F"; } 
                 if ($tags =~ /\bpl\b/) { $nombre = "P"; } 
                 if ($tags =~ /\bsg\b/) { $nombre = "S"; } 
                 my $newtag = $lt_prev.$genere.$nombre.$lt_post;
                 push (@adjs_lt, "$lemme $newtag $flexion");    #lemma tags wordform
                 #print "$lemme $newtag $flexion\n";
             }
        }
    }
} else {
    while (my $line = <$fh>) {
        chomp($line);
        if ($line =~ /(.*) (.*) ($lt_tag_start.*)/) {
            push (@adjs_lt, "$2 $3 $1")
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
    
    if ($line =~ /<e lm="(.*?)".*>.*<[il]>(.*?)<\/[il]>.*<par n="(.*__$apertium_gramcat)"\/><\/e>/) {
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

print STDERR $global_errors;
print STDERR $global_errors2;
print STDERR $global_errors3;

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

    # check lemma in French participles
    if ($lang =~ /^fra$/) {
        my $newlemma = "";
        if ($flexio_lt =~ /AQ0MS0 ([^ ]+)/ ) {
            $newlemma = $1;
            if ($lema !~ /^$newlemma$/) {
                #print STDERR "$lema > $newlemma | $flexio_lt\n";
                $lema = $newlemma;	
            }
        } elsif ($flexio_lt =~ /AQ0MN0 ([^ ]+)/ ) {
            $newlemma = $1;
            if ($lema !~ /^$newlemma$/) {
                #print STDERR "$lema > $newlemma | $flexio_lt\n";
                $lema = $newlemma;	
            }
        }
    }   
 
    my $found = 0;
    for my $rule_name (sort keys %paradigm_names) {
        #print "NOM REGLA: $rule_name\n";
        my $terminacio = $paradigm_names{$rule_name};
        if ($lema =~ /^(.*)$terminacio$/) {
            my $arrel = $1;
            my $flexio_ap = "";
            if (exists $rules_in_oneline{$rule_name}) {
                $flexio_ap = $rules_in_oneline{$rule_name};
                $flexio_ap =~ s/<r>/$arrel/g;
            } else {
                print STDERR "Doesn't exist: $rule_name Lemma: $lema\n";
            }
            $flexio_lt =~ s/(AQA|AO0)/AQ0/g;
            #if ($lema =~ /abatible/) {
            #    print "***** $rule_name $lema $arrel*$flexio_ap*$flexio_lt\n\n";
            #}
            if ($flexio_ap =~ /^$flexio_lt$/) {
                # generate only non existent words
                if (!exists $apertium_dict{$lema}) {
                    print "<e lm=\"$lema\"><i>$arrel</i><par n=\"$rule_name\"/></e>\n";
                    return;
                } else {     # check paradigm
                    if ($apertium_dict{$lema} !~ /^$flexio_lt$/ ) {
                        if ($found==0) {
                            $global_errors .= "\nAPERTIUM: $lema\tPAR: $apertium_dict_paradigm{$lema}\tFORMS: $apertium_dict{$lema}\n";
                        }
                        $global_errors .= "   OTHER: $lema\tPAR: $rule_name\tFORMS: $flexio_lt\n";
                        $found = 1;
                    } else {
                        $found = 1;
                    }
                }

            } 
        }
    }

    if (!exists $apertium_dict{$lema}) {
        $global_errors3 .= "<e lm=\"$lema\"><i>$lema</i><par n=\"??????????\"/></e>\n";
    } else {
        if ($found==0) {
            $global_errors2 .= "\nAPERTIUM: $lema\tPAR: $apertium_dict_paradigm{$lema}\tFORMS: $apertium_dict{$lema}\n";
            $global_errors2 .= "   OTHER: $lema\tPAR: ??????????????\tFORMS: $flexio_lt\n";
        }
    }
}

