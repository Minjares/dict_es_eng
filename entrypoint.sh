#!/bin/bash
# Using absolute paths, no leading dot
/usr/sbin/dictdconfig --write
/etc/init.d/dictd restart
# Execute the main process
exec "$@"

