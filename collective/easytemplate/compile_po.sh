# Compile po files
PRODUCTNAME=collective.easytemplate
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/${PRODUCTNAME}.mo $lang/LC_MESSAGES/${PRODUCTNAME}.po
    fi
done

