#!/bin/sh
find . -name "*.pyc" -type f -delete
echo "compile_ae"
/nz/export/ae/utilities/bin/compile_ae --db $1 --language python \
     --version 3 --template deploy "./put_ht.py" 
echo "copy whole current project"
export AE_PATH="/nz/export/ae/applications/$1/admin"
if [ ! -d $AE_PATH ]; then
    echo "DB doesn't exists"
    exit
fi
rm -rf . $AE_PATH
echo $AE_PATH
yes | cp -rf . $AE_PATH
echo "register_ae"

# każda rejestracja ustawia zmienną środowiskową PUT_FUNC_NAME, która reprezentuje odpowiednią funkcję w klasie PutHT

#predykcja
/nz/export/ae/utilities/bin/register_ae --db $1 --language python --version 3 \
    --template hudtf --exe "./put_ht.py" --sig "PUT_HT_PREDICT_SEQ(VARARGS)" \
    --return "TABLE(predicted_class VARCHAR(1024))" \
    --level 2 \
    --noparallel \
    --environment "'NZAE_LOG_DIR'='/nz/export/ae/log'" \
    --environment "'PUT_FUNC_NAME'='PUT_HT_PREDICT_SEQ'" \
    --environment "'NZAE_REGISTER_NZAE_HOST_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/host/lib'" \
    --environment "'NZAE_REGISTER_NZAE_SPU_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/spu/lib'"

#predykcja równoległa
/nz/export/ae/utilities/bin/register_ae --db $1 --language python --version 3 \
    --template udf --exe "./put_ht.py" --sig "PUT_HT_PREDICT_S(VARARGS)" \
    --return "VARCHAR(1024)" \
    --level 2 \
    --environment "'NZAE_LOG_DIR'='/nz/export/ae/log'" \
    --environment "'PUT_FUNC_NAME'='PUT_HT_PREDICT'" \
    --environment "'NZAE_REGISTER_NZAE_HOST_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/host/lib'" \
    --environment "'NZAE_REGISTER_NZAE_SPU_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/spu/lib'"

#predykcja równoległa
/nz/export/ae/utilities/bin/register_ae --db $1 --language python --version 3 \
    --template hudtf --exe "./put_ht.py" --sig "PUT_HT_PREDICT(VARARGS)" \
    --return "TABLE(predicted_class VARCHAR(1024))" \
    --level 2 \
    --environment "'NZAE_LOG_DIR'='/nz/export/ae/log'" \
    --environment "'PUT_FUNC_NAME'='PUT_HT_PREDICT'" \
    --environment "'NZAE_REGISTER_NZAE_HOST_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/host/lib'" \
    --environment "'NZAE_REGISTER_NZAE_SPU_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/spu/lib'"

#próbkowanie
/nz/export/ae/utilities/bin/register_ae --db $1 --language python --version 3 \
   --template hudtf --exe "./put_ht.py" --sig "PUT_HT_CREATE_AND_PROBE(VARARGS)" \
   --return "TABLE(debug VARCHAR(1024))" \
   --level 2 \
   --noparallel \
   --environment "'NZAE_LOG_DIR'='/nz/export/ae/log'" \
   --environment "'PUT_FUNC_NAME'='PUT_HT_CREATE_AND_PROBE'" \
   --environment "'NZAE_REGISTER_NZAE_HOST_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/host/lib'" \
   --environment "'NZAE_REGISTER_NZAE_SPU_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/spu/lib'"

#trenowanie 
/nz/export/ae/utilities/bin/register_ae --db $1 --language python --version 3 \
    --template hudtf --exe "./put_ht.py" --sig "PUT_HT_TRAIN(VARARGS)" \
    --return "TABLE(debug VARCHAR(1024))" \
    --level 2 \
    --noparallel \
    --environment "'NZAE_LOG_DIR'='/nz/export/ae/log'" \
    --environment "'PUT_FUNC_NAME'='PUT_HT_TRAIN'" \
    --environment "'NZAE_REGISTER_NZAE_HOST_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/host/lib'" \
    --environment "'NZAE_REGISTER_NZAE_SPU_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/spu/lib'"

#czyszczenie klasyfikatora
/nz/export/ae/utilities/bin/register_ae --db $1 --language python --version 3 \
    --template hudtf --exe "./put_ht.py" --sig "PUT_HT_CLEAN(BOOL)" \
    --return "TABLE(state VARCHAR(1024))" \
    --level 2 \
    --noparallel \
    --environment "'NZAE_LOG_DIR'='/nz/export/ae/log'" \
    --environment "'PUT_FUNC_NAME'='PUT_HT_CLEAN'" \
    --environment "'NZAE_REGISTER_NZAE_HOST_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/host/lib'" \
    --environment "'NZAE_REGISTER_NZAE_SPU_ONLY_NZAE_PREPEND_LD_LIBRARY_PATH'='/nz/export/ae/applications/mypython/shared:/nz/export/ae/sysroot/spu/generic/x86_64-generic-linux-gnu/lib/:/nz/export/ae/languages/python/2.6/spu/lib'"

echo "end"