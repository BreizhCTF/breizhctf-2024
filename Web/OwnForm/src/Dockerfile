FROM node:18-alpine

ENV SECRET=d4bd7213707feb6841c1a3864a9ebaaed65976d60eca0ba1bef9d8325892
ENV DOMAIN=localhost
ENV FLAG=BZHCTF{s3lf_xss_c4n_b3_3xpl0it4bl3}
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/lib/chromium/chromium
ENV XDG_CONFIG_HOME=/tmp
ENV XDG_CACHE_HOME=/tmp

WORKDIR /app

COPY package.json package-lock.json ./

RUN  npm install && \
    apk add --no-cache  chromium --repository=http://dl-cdn.alpinelinux.org/alpine/v3.10/main

COPY . .

EXPOSE 443

CMD node index.js