sudo yum -y install zlib-devel openssl-devel cpio expat-devel gettext-devel curl-devel
cd /usr/local/src/hisparc
sudo wget http://git-core.googlecode.com/files/git-1.7.8.tar.gz
sudo tar -xzvf ./git-1.7.8.tar.gz
cd git-1.7.8
sudo ./configure
sudo make
sudo make install 
