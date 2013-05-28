sudo mkdir /usr/local/src/hisparc
sudo chown vagrant /usr/local/src/hisparc
sudo chmod g+w /usr/local/src/hisparc

cd /etc
sudo chmod 777 ld.so.conf.d
cd ld.so.conf.d
cat > /etc/ld.so.conf.d/usrlocal.conf << "EOF"
/usr/local/lib
EOF

sudo yum -y install zlib-devel.x86_64

sudo yum -y install patch

cd /usr/local/src/hisparc
sudo wget http://www.python.org/ftp/python/2.6.4/Python-2.6.4.tgz
sudo tar zxvf Python-2.6.4.tgz
cd Python-2.6.4
sudo make clean
sudo ./configure --enable-shared --prefix=/usr/local
sudo make
sudo make install

sudo ldconfig



# sudo easy_install ipython