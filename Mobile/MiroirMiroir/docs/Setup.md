## Docs 

### Build image

- https://docs.docker.com/reference/dockerfile/#run---security
- https://github.com/docker/buildx/issues/220
- https://github.com/docker/buildx/issues/402

Note install git lfs and checkout the branch first.

```sh
sudo docker buildx create --use --name insecure-builder --buildkitd-flags '--allow-insecure-entitlement security.insecure' 
sudo docker buildx build -t android-emulator:latest --output type=docker,compression=zstd  --allow security.insecure --progress=plain --no-cache .
```

Note : rootless n'expose pas `/dev/kvm`.

## Additional docs

Save the system image : 

```sh
tar -zcvf /share/api_34_android_14_security_2023-09-05.tar.gz system-images/android-34/
google_apis/x86_64/
```

Verify security patch :
```sh
adb shell getprop ro.build.version.security_patch
```