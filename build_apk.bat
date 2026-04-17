@echo off
echo =======================================================
echo     Building Ball Sort APK via Docker Buildozer
echo =======================================================
echo.
echo Please ensure Docker Desktop is running.
echo This process will download the Android SDK, NDK, and compile the Python engine.
echo The very first compile may take 10-15 minutes depending on your internet connection!
echo.
echo Setting up Docker caches to bypass Windows File System limits...
docker volume create buildozer_global_cache
docker volume create buildozer_local_cache
echo.
docker run -e BUILDOZER_WARN_ON_ROOT=0 --rm --volume "%cd%":/home/user/hostcwd --volume buildozer_global_cache:/home/user/.buildozer --volume buildozer_local_cache:/home/user/hostcwd/.buildozer kivy/buildozer android debug
echo.
echo =======================================================
echo Build process concluded!
echo If successful, your .apk file is located in the "bin\" folder.
echo =======================================================
pause
