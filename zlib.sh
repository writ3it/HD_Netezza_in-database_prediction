mkdir /tmp/zlib
mkdir /tmp/zlib/sources
mkdir logs
wget https://zlib.net/zlib-1.2.11.tar.gz --no-check-certificate -O /tmp/zlib/zlib.tar.gz
tar -xzvf /tmp/zlib/zlib.tar.gz -C /tmp/zlib/sources  > logs/zlib.log
