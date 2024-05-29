FROM node:18-alpine

WORKDIR /app

ENV PORT=80
ENV FLAG=BZHCTF{d1d_u_p1ng_m3??}
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/lib/chromium/chromium
ENV XDG_CONFIG_HOME=/tmp
ENV XDG_CACHE_HOME=/tmp

COPY package.json ./

RUN npm install && \
    apk add --no-cache  chromium --repository=http://dl-cdn.alpinelinux.org/alpine/v3.10/main

COPY . .

CMD node index.js
