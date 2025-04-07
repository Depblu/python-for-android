#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dirent.h>
#include <jni.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include "android/log.h"


/*
 * 使用RTLD_GLOBAL标志加载动态库
 */
JNIEXPORT jboolean JNICALL Java_org_kivy_android_PythonUtil_loadLibraryGlobal(
    JNIEnv* env, jclass cls, jstring lib_path)
{
    const char* path = (*env)->GetStringUTFChars(env, lib_path, NULL);
    void* handle = dlopen(path, RTLD_NOW | RTLD_GLOBAL);
    (*env)->ReleaseStringUTFChars(env, lib_path, path);
    
    if (handle == NULL) {
        __android_log_print(ANDROID_LOG_ERROR, "pythonutil", 
                           "Failed to load library with RTLD_GLOBAL: %s (Error: %s)", 
                           path, dlerror());
        return JNI_FALSE;
    }
    
    __android_log_print(ANDROID_LOG_INFO, "pythonutil", 
                       "Successfully loaded library with RTLD_GLOBAL: %s", 
                       path);
    return JNI_TRUE;
}