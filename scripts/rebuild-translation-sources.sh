# Delete old translation sources
find ../src -iname *.po -iwholename */en/* -delete

# Run makemessages on each app
for d in $(find ../src -iwholename */locale/* | sed 's|\(.*\)/locale.*|\1|' | sort -u);
do
    pushd $d
    django-admin makemessages --locale=en
    popd
done
