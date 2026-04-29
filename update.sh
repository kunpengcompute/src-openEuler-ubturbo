#!/bin/sh

set -e

git clone -b br_430 https://gitcode.com/jamesricado/ubturbo.git
cd ubturbo
git log -2
cd ..

rm -rf ubturbo-1.0.0.tar.gz
tar -zcf ubturbo-1.0.0.tar.gz ubturbo/
rm -rf ubturbo/
