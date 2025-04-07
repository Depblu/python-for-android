LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := main

SDL_PATH := ../../SDL

LOCAL_C_INCLUDES := $(LOCAL_PATH)/$(SDL_PATH)/include

# Add your application source files here...
LOCAL_SRC_FILES := $(SDL_PATH)/src/main/android/SDL_android_main.c \
	start.c

LOCAL_CFLAGS += -I$(PYTHON_INCLUDE_ROOT) $(EXTRA_CFLAGS)

LOCAL_SHARED_LIBRARIES := SDL2 python_shared

LOCAL_LDLIBS := -lGLESv1_CM -lGLESv2 -llog $(EXTRA_LDLIBS)

LOCAL_LDFLAGS += -L$(PYTHON_LINK_ROOT) $(APPLICATION_ADDITIONAL_LDFLAGS)

include $(BUILD_SHARED_LIBRARY)



# =====================================================
# Module 2: New 'jni_dlopen_global' library
# =====================================================
include $(CLEAR_VARS)

# Define the name of the new shared library (will be libjni_dlopen_global.so)
LOCAL_MODULE := jni_dlopen_global

# Specify the source file for this library
LOCAL_SRC_FILES := dlopen_global.c

# Add necessary include paths. JNI headers are usually found automatically.
# If you face issues finding jni.h, you might need to add $(NDK_ROOT)/sysroot/usr/include or similar
LOCAL_C_INCLUDES := # Probably empty, unless dlopen_global.c needs specific headers

# Add any compiler flags needed for dlopen_global.c
# Using EXTRA_CFLAGS is a good practice if it contains general flags like optimization/warnings
LOCAL_CFLAGS := $(EXTRA_CFLAGS)

# Specify libraries needed for linking this *specific* module
# -llog is needed for __android_log_print
# -ldl is needed for dlopen, dlerror (part of libdl.so)
LOCAL_LDLIBS := -llog -ldl

# This library likely doesn't depend on SDL2 or Python directly
LOCAL_SHARED_LIBRARIES := # Probably empty

# Build the 'jni_dlopen_global' shared library
include $(BUILD_SHARED_LIBRARY)

# =====================================================