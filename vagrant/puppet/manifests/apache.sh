sudo yum -y install httpd-devel

# cd /etc/httpd/conf
# sudo patch << "EOF"
# --- httpd.conf.orig     2009-12-04 14:35:39.000000000 +0100
# +++ httpd.conf  2009-12-04 14:35:50.000000000 +0100
# @@ -228,8 +228,8 @@
  # when the value of (unsigned)Group is above 60000;
  # don't use Group #-1 on these systems!
 
# -User apache
# -Group apache
# +User www
# +Group www

 ### Section 2: 'Main' server configuration
 #
# EOF

sudo /sbin/chkconfig --add httpd
sudo /sbin/chkconfig --levels 35 httpd on

sudo /sbin/service httpd start 
 
cd /usr/local/src/hisparc
sudo wget http://modwsgi.googlecode.com/files/mod_wsgi-3.1.tar.gz
sudo tar xvzf mod_wsgi-3.1.tar.gz
cd mod_wsgi-3.1
sudo ./configure --enable-shared --prefix=/usr/local
sudo make
sudo make install
 
# cd /etc/httpd/conf
 
# sudo patch << "EOF"
# --- httpd.conf.orig     2009-12-04 15:19:01.000000000 +0100
# +++ httpd.conf  2009-12-04 15:34:30.000000000 +0100
# @@ -197,6 +197,7 @@
 # LoadModule mem_cache_module modules/mod_mem_cache.so
 # LoadModule cgi_module modules/mod_cgi.so
 # LoadModule version_module modules/mod_version.so
# +LoadModule wsgi_module modules/mod_wsgi.so

 #
 # The following modules are not loaded by default:
# EOF



sudo /sbin/service httpd restart