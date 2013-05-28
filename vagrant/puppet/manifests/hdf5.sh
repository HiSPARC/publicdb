cd /usr/local/src/hisparc
wget http://www.hdfgroup.org/ftp/HDF5/prev-releases/hdf5-1.8.3/src/hdf5-1.8.3.tar.gz
tar xvzf hdf5-1.8.3.tar.gz
cd hdf5-1.8.3
./configure --enable-shared --prefix=/usr/local
make
sudo make install
sudo ldconfig