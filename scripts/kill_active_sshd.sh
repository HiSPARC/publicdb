TTY=`tty | sed 's/\/dev\///'`
PID=`ps x | grep "sshd.*$TTY" | head -n 1 | awk '{print $1}'`
kill $PID
