alias turnOffScreen='if adb shell dumpsys input_method | grep -q "mInteractive=true"; then adb shell input keyevent KEYCODE_POWER;fi && while adb shell dumpsys input_method | grep -q "mInteractive=true"; do sleep 0.1; done'
alias ensureScreenIsLocked='while adb shell dumpsys power | grep -q "mUserActivityTimeoutOverrideFromWindowManager=-1"; do sleep 0.1; done && sleep 1'

# We want to setup a "default_boot" snapshot for fast boots in the container
yes '' | avdmanager create avd -n "${AVD_NAME}" -k "${AVD_SYSTEM_IMAGE}" &&
    emulator -avd "${AVD_NAME}" -no-window -no-audio -no-boot-anim -no-snapshot -wipe-data -verbose &
adb wait-for-device shell 'while [[ -z $(getprop sys.boot_completed) ]]; do sleep 1; done;' &&
    adb shell locksettings set-password "$(openssl rand -hex 8)" &&
    sleep 5 &&
    turnOffScreen &&
    ensureScreenIsLocked &&
    sleep 5 &&
    adb emu avd snapshot save post_setup &&
    adb shell reboot -p
