# syntax=docker/dockerfile:1-labs
FROM node:21-bookworm AS snapshot_builder

RUN apt-get update

# Setup Android SDK
RUN apt-get install -y openjdk-17-jdk gradle unzip wget openssl
RUN mkdir -p /opt/Android/cmdline-tool
RUN wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O commandlinetools.zip
RUN unzip commandlinetools.zip -d /opt/Android/cmdline-tools
RUN mv /opt/Android/cmdline-tools/cmdline-tools /opt/Android/cmdline-tools/latest
RUN rm commandlinetools.zip

ENV ANDROID_HOME /opt/Android
ENV PATH "${ANDROID_HOME}/emulator:${ANDROID_HOME}/cmdline-tools/latest:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/tools:${ANDROID_HOME}/tools/bin:${PATH}"
ENV AVD_SYSTEM_IMAGE "system-images;android-34;google_apis;x86_64"
ENV AVD_NAME "challenge_avd"
RUN yes | sdkmanager --licenses \
    && sdkmanager "build-tools;34.0.0" "platform-tools" "platforms;android-34" "tools"

COPY api_34_android_14_security_2023-09-05.tar.gz .
RUN tar xvf api_34_android_14_security_2023-09-05.tar.gz -C /opt/Android/
RUN rm api_34_android_14_security_2023-09-05.tar.gz

RUN --security=insecure emulator -accel-check || exit 1
COPY snapshot_emulator.sh /tmp/snapshot_emulator.sh
RUN chmod +x /tmp/snapshot_emulator.sh
RUN --security=insecure /tmp/snapshot_emulator.sh

FROM node:21-bookworm AS node_builder

COPY package.json yarn.lock tsconfig.json /challenge/
COPY ./src /challenge/src

WORKDIR /challenge
RUN yarn
RUN yarn tsc

FROM node:21-bookworm

# Setup Android SDK
RUN apt-get update && apt-get install -y openjdk-17-jdk gradle openssl

RUN useradd -u 666 --home=/challenge -U challenge
RUN groupadd -g 992 -U challenge kvm

COPY --from=snapshot_builder /opt/Android /opt/Android
COPY --from=snapshot_builder --chown=challenge:challenge /root/.android/ /challenge/.android/
RUN find /challenge/.android/ -name '*.lock' -delete

ENV ANDROID_HOME /opt/Android
ENV PATH "${ANDROID_HOME}/emulator:${ANDROID_HOME}/cmdline-tools/latest:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/tools:${ANDROID_HOME}/tools/bin:${PATH}"
ENV AVD_SYSTEM_IMAGE "system-images;android-34;google_apis;x86_64"
ENV AVD_NAME "challenge_avd"

# Copy challenge files to container build
COPY flag_1a2a7.apk package.json yarn.lock /challenge/
COPY src/static /challenge/static
COPY src/templates /challenge/templates
COPY --from=node_builder /challenge/bin /challenge

WORKDIR /challenge
RUN yarn install --production

USER challenge

# Entrypoint
ENTRYPOINT ["node"]
CMD ["index.js"]
