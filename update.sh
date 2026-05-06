#!/bin/sh

set -e

git clone https://atomgit.com/openeuler/ubturbo.git
cd ubturbo
git log -2
cd ..

rm -rf ubturbo-1.0.0.tar.gz
tar -zcf ubturbo-1.0.0.tar.gz ubturbo/
rm -rf ubturbo/
