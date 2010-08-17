if [[ $# == 0 ]]; then
    version=`python -c "import do3se.application ; print do3se.application.app_version"`
elif [[ $# == 1 ]]; then
    version=$1
else
    echo "Usage: sh build-gui-win32.sh [VERSION]"
fi

distdir="DO3SE-${version}"
archive="${distdir}.zip"

echo "Building ${distdir} (${archive})"

# Remove existing built files
rm -rf build "${distdir}" "${archive}"
# Build the GUI
python setup.py py2exe -d ${distdir}
# Package it into a .zip
7za a -tzip "${archive}" "${distdir}"
