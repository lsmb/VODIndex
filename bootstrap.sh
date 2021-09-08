#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" ]; then
    echo "We're on a MAC!"
   chromeDriver="chromedriver_mac64.zip"
   geckoDriverVersion="v0.24.0"
   geckoDriver="geckodriver-$geckoDriverVersion-macos.tar.gz"
else
    echo "We're not on a MAC!"
   chromeDriver="chromedriver_linux64.zip"
   geckoDriverVersion="v0.24.0"
   geckoDriver="geckodriver-$geckoDriverVersion-linux64.tar.gz"
fi
rm -rf tools
mkdir -p tools && \
cd tools && \
wget https://github.com/browserup/browserup-proxy/releases/download/v1.1.0/browserup-proxy-1.1.0.zip && \
unzip -o browserup-proxy-1.1.0.zip && \
rm -rf browserup-proxy*.zip* && \
wget https://selenium-release.storage.googleapis.com/3.141/selenium-server-standalone-3.141.59.jar && \
wget https://github.com/mozilla/geckodriver/releases/download/${geckoDriverVersion}/${geckoDriver} && \
tar zxf ${geckoDriver} && \
rm -rf ${geckoDriver}* && \
wget https://chromedriver.storage.googleapis.com/74.0.3729.6/${chromeDriver} && \
unzip ${chromeDriver} && \
rm -rf ${chromeDriver}* && \
cd ..
