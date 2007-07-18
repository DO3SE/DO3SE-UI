FEXEC="/usr/local/bin/F"

${FEXEC} -o original Baum_DOSE.f90
${FEXEC} -o modular DOSE_module.f90 DOSE_file.f90

./original
./modular

diff -u 2003_output test_output
