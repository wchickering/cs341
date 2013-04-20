#!/usr/bin/perl -w

use strict;

while (<>) {
    my ($itemid, $deltaQueryIdsStr) = split /\t/, $_;
    my @deltaQueryId = split /,/, $deltaQueryIdsStr;
    for (my $i = 1; $i < @deltaQueryId; $i++) {
        $deltaQueryId[$i] += $deltaQueryId[$i-1];
    }
    print "$itemid\t".join(',',@deltaQueryId)."\n";
}

