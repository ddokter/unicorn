# Unicorn

Django app for interpreting beer recipes from before the era of metric units.

Do you remember the good old days, when every city had it's own ways
of measuring, weighing and torturing? Well, I sure as hell don't. Born
and raised in the era of the metric system, I suffer some trouble when
reading _recipes_ (in reality more like legal prescriptions) like:

    Vander Koyten. Selmen brouwen dubbelde koyte, elc brout XVIII
    grove vate, als elc vat van X eymeren, die maken XXII½ smaell
    vate. Ende dair sellen sij in verbrouwen ende in laten XII mudde
    haveren, VI mudde garsten ende drije mudde weyts.

even if I __do__ read 15th century Dutch without too much trouble. So, to
brew a Double Koyt, we need 12 mud oats, 6 mud barley and 3 mud, to
end up with a brew size of 18 barrels, each 10 buckets, or 22.5 small
barrels. Well, well, well.

Unicorn enables you to convert the recipes you find to the metric
units that we so conveniently use today. It does this by using all
kinds of observations in classic and modern literature about what the
one unit from that specific city was, in relation to that other
unit. If all is well, the system will find a relation to metric units
somewhere down the line. If not, find more sources and add conversions...
