# Set UseDNS No in /etc/ssh/sshd_config
# Prevent reverse DNS lookup for SSH connections to VMs
# Connections may be slow or timeout when the default is used.
#
# regex:
# ^         match start of line
# #\?       match a single # (comment) or none
# \ \?      match a single space or none
# UseDNS .* match anything starting with "UseDNS "
#
# replace with "UseDNS No"
sed -i 's/^#\?\ \?UseDNS .*/UseDNS no/' /etc/ssh/sshd_config
grep UseDNS /etc/ssh/sshd_config
