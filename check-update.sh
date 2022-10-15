#!/bin/sh
curl -L https://uclibc-ng.org/ 2>/dev/null |grep -E 'uClibc-ng-[0-9\.]*\.tar\.xz' |head -n1 |sed -e 's,.*releases/,,;s,/.*,,'
