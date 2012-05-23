DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
    },
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'refinery.sqlite',
#     },
# }
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'refinery'
]