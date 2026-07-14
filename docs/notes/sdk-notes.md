export ANDROID_HOME=${HOME}/.android/
export JAVA_HOME=${ANDROID_HOME}jdk-17.0.2/
export PATH=${JAVA_HOME}bin:$PATH
export PATH=${ANDROID_HOME}cmdline-tools/latest/bin:$PATH
export PATH=${ANDROID_HOME}platform-tools:$PATH
export PATH=${ANDROID_HOME}emulator:$PATH
export PATH=${ANDROID_HOME}scrcpy:$PATH
export PATH=${ANDROID_HOME}jadx/bin:$PATH
export PATH=${ANDROID_HOME}misc-tools:$PATH

# Version agnostic PATH entries and symlink to fallback build-tools
export PATH=$PATH:${ANDROID_HOME}misc-tools/build-tools-symlink

# Make sure .android and .android/scripts exists.
ls ${ANDROID_HOME}misc-tools &>/dev/null || mkdir -p ${ANDROID_HOME}misc-tools
# Assuming build-tools 33.0.0 manually installed.
ls ${ANDROID_HOME}misc-tools/build-tools-symlink &>/dev/null \
  || ln -s ${ANDROID_HOME}build-tools/33.0.0 ${ANDROID_HOME}misc-tools/build-tools-symlink

export PS1_TAG="(adb-venv) "
export PS1="${PS1_TAG}${PS1:-\$ }"