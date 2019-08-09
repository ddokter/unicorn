# Unicorn

Django app for interpreting beer recipes from before the era of metric units.

Do you remember the good old days, when every city had it's own ways
of measuring, weighing and torturing? Well, I sure as hell don't and I
really doubt whether they were all that good. Born and raised in the
era of the metric system, I suffer some trouble when reading _recipes_
(in reality more like legal prescriptions) like:

    Vander Koyten. Selmen brouwen dubbelde koyte, elc brout XVIII
    grove vate, als elc vat van X eymeren, die maken XXII½ smaell
    vate. Ende dair sellen sij in verbrouwen ende in laten XII mudde
    haveren, VI mudde garsten ende drije mudde weyts.

even if I __do__ read 15th century Dutch without too much trouble. So, to
brew a Double Koyt, we need 12 mud oats, 6 mud barley and 3 mud wheat, to
end up with a brew size of 18 barrels, each 10 buckets, or 22.5 small
barrels. Well, well, well.

Unicorn enables you to convert the recipes you find to the metric
units that we so conveniently use today. It does this by using all
kinds of observations in classic and modern literature about what the
one unit from that specific city was, in relation to that other
unit. If all is well, the system will find a relation to metric units
somewhere down the line. If not, find more sources and add conversions...


## Installation

There is many ways to get up and running with Django apps. I'll give you one,
always assuming you run a serious OS like Debian or so:

1. Create a virtual environment:

    mkdir VENV
    cd VENV
    virtualenv --python=python3.7 VENV

2. Activate it

    cd VENV
    . bin/activate

3. Now you have a nice sandbox, to play around in without destroying your
   system. Unless you use Micro$oft, of course. Install the needed software:

    pip install https://github.com/ddokter/beerlab/archive/master.zip
    pip install https://github.com/ddokter/unicorn/archive/develop.zip

4. Create a Django instance:

   django-admin startproject <your own fancy project name>

5. Edit settings, (in ./foo/foo/settings.py) of the project you just created,
   and of course aptly named 'foo'.

    INSTALLED_APPS = [
      ...
      'bootstrap4',
      'unicorn'
    ]

    BOOTSTRAP4 = {
      "css_url": {
        "href": "/static/bootstrap/css/bootstrap.css"
     },
     'include_jquery': True,
     "javascript_url": {
       "url": "/static/bootstrap/js/bootstrap.bundle.js"
     },
     "jquery_url": {
       "url": "/static/bootstrap/js/jquery-3.2.1.js"
     }
    }

6. Edit URLS in ./foo/foo/urls.py, add unicorn urls to existing list, and
    import include:

    from django.urls import include

    urlpatterns = [
      ...
      path('', include('unicorn.urls'))
    ]

7. Rev up the engine:

    cd ./foo
    ./manage migrate
    ./manage runserver

8. Start your favority browser (probably Lynx) and navigate to:

    http://localhost:8000/

and there you have it.
