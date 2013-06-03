cd /usr/local/src/hisparc
cd Python-2.6.4
sudo make clean
sudo ./configure --enable-shared --prefix=/usr/local
sudo make
sudo make install