#!/usr/bin/env bash
# Prepares SVGs exported from Penpot for the repository: drops every <style> block with an
# @font-face rule (it loads fonts from Penpot's servers) and appends the system fallbacks from
# tokens.json to a font family named alone, so text renders the same on GitHub and offline.
# Running it twice changes nothing.
# Usage: bash docs/design/postprocess-svg.sh [docs/diagrams/<name>.svg ...]   (default: every SVG)
set -euo pipefail
design="$(dirname "$0")"

[ "$#" -gt 0 ] || set -- "$design"/../diagrams/*.svg
[ -e "$1" ] || { echo "no SVG to process"; exit 0; }

TOKENS="$design/tokens.json" perl -MJSON::PP -e '
  open my $in, "<", $ENV{TOKENS} or die "cannot read $ENV{TOKENS}\n";
  my $font = decode_json(do { local $/; <$in> })->{font};
  my $name = sub { $_[0] =~ / / ? "'"'"'$_[0]'"'"'" : $_[0] };
  my @stacks = ([$font->{family}, $font->{fallback}]);
  push @stacks, [$font->{mono}, $font->{"mono-fallback"}] if $font->{mono};
  my $quote = q{(?:&quot;|'"'"'|")?};
  for my $file (@ARGV) {
    open my $fh, "<:raw", $file or die "cannot read $file\n";
    my $before = do { local $/; <$fh> };
    close $fh;
    my $svg = $before;
    $svg =~ s{<style[^>]*>(?:(?!</style>).)*?\@font-face.*?</style>}{}gs;
    for (@stacks) {
      my ($family, $fallback) = @$_;
      my $stack = join ", ", map { $name->($_) } $family, @$fallback;
      # Only a family named alone is rewritten, so a second run finds nothing to change.
      $svg =~ s{font-family:\s*$quote\Q$family\E$quote\s*(?=[;"\}])}{font-family: $stack}g;
      $svg =~ s{font-family="$quote\Q$family\E$quote"}{font-family="$stack"}g;
    }
    if ($svg ne $before) {
      open my $out, ">:raw", $file or die "cannot write $file\n";
      print $out $svg;
      close $out;
    }
    print +($svg eq $before ? "unchanged" : "processed"), " $file\n";
  }
' "$@"
