sudo mkdir /srv/publicdb/publicdb_env/bin/hisparc
sudo chown vagrant /srv/publicdb/publicdb_env/bin/hisparc
sudo chmod g+w /srv/publicdb/publicdb_env/bin/hisparc

cd /usr/local/src/hisparc
sudo wget http://www.hdfgroup.org/ftp/HDF5/prev-releases/hdf5-1.8.9/src/hdf5-1.8.9.tar.gz
sudo tar xvzf hdf5-1.8.9.tar.gz
cd hdf5-1.8.9
sudo patch << EOF
--- CMakeLists.txt (revision 22471)
+++ CMakeLists.txt (working copy)
@@ -884,7 +884,7 @@
-        ${HDF5_SOURCE_DIR}/release_docs/Using_CMake.txt
+        ${HDF5_SOURCE_DIR}/release_docs/USING_CMake.txt
EOF
sudo ./configure --prefix=/usr/local
sudo make
sudo make install
