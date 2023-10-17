export CIBW_BUILD="{cp38,cp39,cp310}-manylinux_x86_64"
cibuildwheel --platform linux
