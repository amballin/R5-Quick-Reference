#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <EDSDK.h>

static EdsCameraRef g_camera = NULL;
static int g_session_open = 0;
static int g_sdk_initialized = 0;
static int g_physical_writes_enabled = 0;

static EdsError EDSCALLBACK property_event_handler(
    EdsPropertyEvent event,
    EdsPropertyID property,
    EdsUInt32 parameter,
    EdsVoid *context
) {
    (void)event;
    (void)property;
    (void)parameter;
    (void)context;
    return EDS_ERR_OK;
}

static EdsError pump_camera_events(void) {
    return EdsGetEvent();
}

static void json_string(const char *value) {
    const unsigned char *cursor;
    if (value == NULL) {
        fputs("null", stdout);
        return;
    }
    putchar('"');
    for (cursor = (const unsigned char *)value; *cursor != '\0'; cursor++) {
        switch (*cursor) {
            case '"': fputs("\\\"", stdout); break;
            case '\\': fputs("\\\\", stdout); break;
            case '\b': fputs("\\b", stdout); break;
            case '\f': fputs("\\f", stdout); break;
            case '\n': fputs("\\n", stdout); break;
            case '\r': fputs("\\r", stdout); break;
            case '\t': fputs("\\t", stdout); break;
            default:
                if (*cursor < 0x20) {
                    fprintf(stdout, "\\u%04x", *cursor);
                } else {
                    putchar(*cursor);
                }
        }
    }
    putchar('"');
}

static void emit_error(const char *operation, EdsError error) {
    fputs("{\"ok\":false,\"operation\":", stdout);
    json_string(operation);
    fprintf(stdout, ",\"code\":%u}\n", (unsigned int)error);
    fflush(stdout);
}

static void close_camera(void) {
    if (g_camera != NULL) {
        if (g_session_open) {
            EdsCloseSession(g_camera);
            g_session_open = 0;
        }
        EdsRelease(g_camera);
        g_camera = NULL;
    }
}

static void cleanup(void) {
    close_camera();
    if (g_sdk_initialized) {
        EdsTerminateSDK();
        g_sdk_initialized = 0;
    }
}

static int read_string(EdsCameraRef camera, EdsPropertyID property, char *buffer, EdsUInt32 size) {
    EdsError error;
    memset(buffer, 0, size);
    error = EdsGetPropertyData(camera, property, 0, size, buffer);
    return error == EDS_ERR_OK && buffer[0] != '\0';
}

static int read_uint32(EdsCameraRef camera, EdsPropertyID property, EdsUInt32 *value) {
    EdsError error = EdsGetPropertyData(camera, property, 0, sizeof(*value), value);
    return error == EDS_ERR_OK;
}

typedef struct {
    const char *key;
    const char *label;
    EdsPropertyID property;
} CapabilitySpec;

static const CapabilitySpec CAPABILITY_SPECS[] = {
    {"battery_level", "Battery / power", kEdsPropID_BatteryLevel},
    {"storage_destination", "Storage destination", kEdsPropID_SaveTo},
    {"image_quality", "Image quality", kEdsPropID_ImageQuality},
    {"white_balance", "White balance", kEdsPropID_WhiteBalance},
    {"color_space", "Color space", kEdsPropID_ColorSpace},
    {"picture_style", "Picture style", kEdsPropID_PictureStyle},
    {"exposure_mode", "Exposure mode", kEdsPropID_AEMode},
    {"drive_mode", "Drive mode", kEdsPropID_DriveMode},
    {"iso_speed", "ISO speed", kEdsPropID_ISOSpeed},
    {"metering_mode", "Metering mode", kEdsPropID_MeteringMode},
    {"af_mode", "AF operation", kEdsPropID_AFMode},
    {"aperture", "Aperture", kEdsPropID_Av},
    {"shutter_speed", "Shutter speed", kEdsPropID_Tv},
    {"exposure_compensation", "Exposure compensation", kEdsPropID_ExposureCompensation},
    {"available_shots", "Available shots", kEdsPropID_AvailableShots},
    {"noise_reduction", "Noise reduction (image metadata property)", kEdsPropID_NoiseReduction},
    {"ibis_high_res_shot", "IBIS high-resolution shot", kEdsPropID_IBIS_HighResoShot},
    {"af_method", "AF method / area", kEdsPropID_Evf_AFMode},
    {"cropping_aspect_ratio", "Cropping / aspect ratio", kEdsPropID_Aspect},
    {"continuous_af", "Preview AF / continuous AF", kEdsPropID_ContinuousAfMode},
    {"eye_detection", "Eye detection", kEdsPropID_AFEyeDetect},
    {"subject_detection", "Subject to detect", kEdsPropID_AFTrackingObject}
};

static const CapabilitySpec *find_capability(const char *key) {
    size_t index;
    for (index = 0; index < sizeof(CAPABILITY_SPECS) / sizeof(CAPABILITY_SPECS[0]); index++) {
        if (strcmp(CAPABILITY_SPECS[index].key, key) == 0) {
            return &CAPABILITY_SPECS[index];
        }
    }
    return NULL;
}

static int is_write_qualification_candidate(const char *key) {
    static const char *CANDIDATES[] = {
        "white_balance", "picture_style", "drive_mode", "metering_mode", "af_mode",
        "af_method", "cropping_aspect_ratio", "continuous_af", "eye_detection"
    };
    size_t index;
    for (index = 0; index < sizeof(CANDIDATES) / sizeof(CANDIDATES[0]); index++) {
        if (strcmp(CANDIDATES[index], key) == 0) return 1;
    }
    return 0;
}

typedef struct {
    EdsPropertyID property;
    EdsUInt32 activation_code;
} LimitedPropertySpec;

/*
 * Canon documents these calls as pre-session property activation. They expose
 * read access to limited properties and do not set a camera menu value. Errors
 * are intentionally non-fatal because support is camera-model dependent.
 */
static const LimitedPropertySpec LIMITED_PROPERTY_SPECS[] = {
    {kEdsPropID_Aspect, 0x3FB1718B},
    {kEdsPropID_AFEyeDetect, 0x7C89405C},
    {kEdsPropID_AFTrackingObject, 0x0C78510D},
    {kEdsPropID_ContinuousAfMode, 0x32F87FF6}
};

static void activate_limited_properties(EdsCameraRef camera) {
    size_t index;
    for (index = 0; index < sizeof(LIMITED_PROPERTY_SPECS) / sizeof(LIMITED_PROPERTY_SPECS[0]); index++) {
        EdsUInt32 property = (EdsUInt32)LIMITED_PROPERTY_SPECS[index].property;
        EdsSetPropertyData(
            camera,
            0x01000000,
            (EdsInt32)LIMITED_PROPERTY_SPECS[index].activation_code,
            sizeof(property),
            &property
        );
    }
}

static const char *data_type_name(EdsDataType data_type) {
    switch (data_type) {
        case kEdsDataType_Bool: return "bool";
        case kEdsDataType_String: return "string";
        case kEdsDataType_Int8: return "int8";
        case kEdsDataType_UInt8: return "uint8";
        case kEdsDataType_Int16: return "int16";
        case kEdsDataType_UInt16: return "uint16";
        case kEdsDataType_Int32: return "int32";
        case kEdsDataType_UInt32: return "uint32";
        case kEdsDataType_Int64: return "int64";
        case kEdsDataType_UInt64: return "uint64";
        case kEdsDataType_Float: return "float";
        case kEdsDataType_Double: return "double";
        case kEdsDataType_ByteBlock: return "byte_block";
        default: return "other";
    }
}

static const char *access_name(EdsInt32 access) {
    switch (access) {
        case 0: return "read";
        case 1: return "write";
        case 2: return "read_write";
        default: return "unknown";
    }
}

static void emit_hex_value(const unsigned char *buffer, EdsUInt32 size) {
    EdsUInt32 index;
    putchar('"');
    for (index = 0; index < size; index++) {
        fprintf(stdout, "%02x", buffer[index]);
    }
    putchar('"');
}

static void emit_typed_value(EdsDataType data_type, const void *buffer, EdsUInt32 size) {
    if (data_type == kEdsDataType_String) {
        json_string((const char *)buffer);
    } else if ((data_type == kEdsDataType_Bool || data_type == kEdsDataType_UInt32) && size >= sizeof(EdsUInt32)) {
        fprintf(stdout, "%u", (unsigned int)*(const EdsUInt32 *)buffer);
    } else if (data_type == kEdsDataType_Int32 && size >= sizeof(EdsInt32)) {
        fprintf(stdout, "%lld", (long long)*(const EdsInt32 *)buffer);
    } else if (data_type == kEdsDataType_UInt16 && size >= sizeof(EdsUInt16)) {
        fprintf(stdout, "%u", (unsigned int)*(const EdsUInt16 *)buffer);
    } else if (data_type == kEdsDataType_Int16 && size >= sizeof(EdsInt16)) {
        fprintf(stdout, "%d", (int)*(const EdsInt16 *)buffer);
    } else if (data_type == kEdsDataType_UInt8 && size >= sizeof(EdsUInt8)) {
        fprintf(stdout, "%u", (unsigned int)*(const EdsUInt8 *)buffer);
    } else if (data_type == kEdsDataType_Int8 && size >= sizeof(EdsInt8)) {
        fprintf(stdout, "%d", (int)*(const EdsInt8 *)buffer);
    } else if (data_type == kEdsDataType_UInt64 && size >= sizeof(EdsUInt64)) {
        fprintf(stdout, "%llu", (unsigned long long)*(const EdsUInt64 *)buffer);
    } else if (data_type == kEdsDataType_Int64 && size >= sizeof(EdsInt64)) {
        fprintf(stdout, "%lld", (long long)*(const EdsInt64 *)buffer);
    } else {
        fputs("null", stdout);
    }
}

static void emit_capability(const CapabilitySpec *spec) {
    EdsDataType data_type = kEdsDataType_Unknown;
    EdsUInt32 size = 0;
    EdsError read_error = EdsGetPropertySize(g_camera, spec->property, 0, &data_type, &size);
    unsigned char *buffer = NULL;
    EdsPropertyDesc descriptor;
    EdsError descriptor_error;
    EdsInt32 descriptor_count;
    EdsInt32 index;

    if (read_error == EDS_ERR_OK && size > 0 && size <= 4096) {
        buffer = (unsigned char *)calloc(1, size + 1);
        if (buffer == NULL) {
            read_error = EDS_ERR_MEM_ALLOC_FAILED;
        } else {
            read_error = EdsGetPropertyData(g_camera, spec->property, 0, size, buffer);
        }
    } else if (read_error == EDS_ERR_OK) {
        read_error = EDS_ERR_NOT_SUPPORTED;
    }

    memset(&descriptor, 0, sizeof(descriptor));
    descriptor_error = EdsGetPropertyDesc(g_camera, spec->property, &descriptor);
    descriptor_count = descriptor.numElements;
    if (descriptor_count < 0) descriptor_count = 0;
    if (descriptor_count > 128) descriptor_count = 128;

    fputs("{\"key\":", stdout);
    json_string(spec->key);
    fputs(",\"label\":", stdout);
    json_string(spec->label);
    fprintf(stdout, ",\"property_id\":%u,\"property_id_hex\":\"0x%08x\"", (unsigned int)spec->property, (unsigned int)spec->property);
    fputs(",\"read_status\":", stdout);
    json_string(read_error == EDS_ERR_OK ? "sdk_verified" : "unreadable");
    fprintf(stdout, ",\"read_error\":");
    if (read_error == EDS_ERR_OK) fputs("null", stdout); else fprintf(stdout, "%u", (unsigned int)read_error);
    fputs(",\"data_type\":", stdout);
    json_string(data_type_name(data_type));
    fprintf(stdout, ",\"data_type_raw\":%d,\"size\":%u,\"value_raw\":", (int)data_type, (unsigned int)size);
    if (read_error == EDS_ERR_OK) emit_typed_value(data_type, buffer, size); else fputs("null", stdout);
    fputs(",\"value_hex\":", stdout);
    if (read_error == EDS_ERR_OK) emit_hex_value(buffer, size); else fputs("null", stdout);
    fputs(",\"descriptor_status\":", stdout);
    json_string(descriptor_error == EDS_ERR_OK ? "sdk_verified" : "unavailable");
    fputs(",\"descriptor_error\":", stdout);
    if (descriptor_error == EDS_ERR_OK) fputs("null", stdout); else fprintf(stdout, "%u", (unsigned int)descriptor_error);
    fputs(",\"descriptor_access\":", stdout);
    if (descriptor_error == EDS_ERR_OK) json_string(access_name(descriptor.access)); else fputs("null", stdout);
    fputs(",\"descriptor_access_raw\":", stdout);
    if (descriptor_error == EDS_ERR_OK) fprintf(stdout, "%lld", (long long)descriptor.access); else fputs("null", stdout);
    fputs(",\"descriptor_form\":", stdout);
    if (descriptor_error == EDS_ERR_OK) fprintf(stdout, "%lld", (long long)descriptor.form); else fputs("null", stdout);
    fputs(",\"allowed_values_raw\":[", stdout);
    if (descriptor_error == EDS_ERR_OK) {
        for (index = 0; index < descriptor_count; index++) {
            if (index > 0) putchar(',');
            fprintf(stdout, "%lld", (long long)descriptor.propDesc[index]);
        }
    }
    fputs("],\"write_tested\":false}", stdout);
    free(buffer);
}

static void emit_capabilities(void) {
    size_t index;
    EdsError event_error;
    if (g_camera == NULL || !g_session_open) {
        emit_error("CapabilitiesWithoutSession", EDS_ERR_NOT_SUPPORTED);
        return;
    }
    event_error = pump_camera_events();
    if (event_error != EDS_ERR_OK) {
        emit_error("EdsGetEvent(Capabilities)", event_error);
        return;
    }
    fputs("{\"ok\":true,\"properties\":[", stdout);
    for (index = 0; index < sizeof(CAPABILITY_SPECS) / sizeof(CAPABILITY_SPECS[0]); index++) {
        if (index > 0) putchar(',');
        emit_capability(&CAPABILITY_SPECS[index]);
    }
    fputs("]}\n", stdout);
    fflush(stdout);
}

static void write_qualified_candidate(const char *key, EdsUInt32 value) {
    const CapabilitySpec *spec = find_capability(key);
    EdsPropertyDesc descriptor;
    EdsDataType data_type = kEdsDataType_Unknown;
    EdsUInt32 size = 0;
    EdsError error;
    EdsInt32 index;
    int allowed = 0;

    if (!g_physical_writes_enabled) {
        emit_error("PhysicalWritesNotEnabled", EDS_ERR_NOT_SUPPORTED);
        return;
    }
    if (g_camera == NULL || !g_session_open) {
        emit_error("WriteWithoutSession", EDS_ERR_NOT_SUPPORTED);
        return;
    }
    if (spec == NULL || !is_write_qualification_candidate(key)) {
        emit_error("WritePropertyNotAllowlisted", EDS_ERR_NOT_SUPPORTED);
        return;
    }
    error = pump_camera_events();
    if (error != EDS_ERR_OK) {
        emit_error("EdsGetEvent(BeforeWrite)", error);
        return;
    }
    error = EdsGetPropertySize(g_camera, spec->property, 0, &data_type, &size);
    if (error != EDS_ERR_OK) {
        emit_error("EdsGetPropertySize(Write)", error);
        return;
    }
    if (size != sizeof(EdsUInt32) || (data_type != kEdsDataType_UInt32 && data_type != kEdsDataType_Int32)) {
        emit_error("UnsupportedWriteDataType", EDS_ERR_NOT_SUPPORTED);
        return;
    }
    memset(&descriptor, 0, sizeof(descriptor));
    error = EdsGetPropertyDesc(g_camera, spec->property, &descriptor);
    if (error != EDS_ERR_OK) {
        emit_error("EdsGetPropertyDesc(Write)", error);
        return;
    }
    for (index = 0; index < descriptor.numElements && index < 128; index++) {
        if ((EdsUInt32)descriptor.propDesc[index] == value) {
            allowed = 1;
            break;
        }
    }
    if (!allowed) {
        emit_error("WriteValueNotInDescriptor", EDS_ERR_NOT_SUPPORTED);
        return;
    }
    error = EdsSetPropertyData(g_camera, spec->property, 0, sizeof(value), &value);
    if (error != EDS_ERR_OK) {
        emit_error("GuardedPropertyWrite", error);
        return;
    }
    error = pump_camera_events();
    if (error != EDS_ERR_OK) {
        emit_error("EdsGetEvent(AfterWrite)", error);
        return;
    }
    fputs("{\"ok\":true,\"property_key\":", stdout);
    json_string(key);
    fprintf(stdout, ",\"value_raw\":%u}\n", (unsigned int)value);
    fflush(stdout);
}

static void emit_camera_details(EdsCameraRef camera) {
    char product[256];
    char body_id[256];
    char firmware[256];
    char lens_name[256];
    EdsUInt32 battery = 0;
    int has_product = read_string(camera, kEdsPropID_ProductName, product, sizeof(product));
    int has_body_id = read_string(camera, kEdsPropID_BodyIDEx, body_id, sizeof(body_id));
    int has_firmware = read_string(camera, kEdsPropID_FirmwareVersion, firmware, sizeof(firmware));
    int has_lens_name = read_string(camera, kEdsPropID_LensName, lens_name, sizeof(lens_name));
    int has_battery = read_uint32(camera, kEdsPropID_BatteryLevel, &battery);

    fputs("{\"ok\":true,\"product_name\":", stdout);
    json_string(has_product ? product : NULL);
    fputs(",\"body_id\":", stdout);
    json_string(has_body_id ? body_id : NULL);
    fputs(",\"firmware_version\":", stdout);
    json_string(has_firmware ? firmware : NULL);
    fputs(",\"lens_name\":", stdout);
    json_string(has_lens_name ? lens_name : NULL);
    if (has_battery) {
        fprintf(stdout, ",\"battery_raw\":%u", (unsigned int)battery);
    } else {
        fputs(",\"battery_raw\":null", stdout);
    }
    fputs("}\n", stdout);
    fflush(stdout);
}

static void discover_cameras(void) {
    EdsCameraListRef list = NULL;
    EdsUInt32 count = 0;
    EdsError error = EdsGetCameraList(&list);
    EdsUInt32 index;
    if (error != EDS_ERR_OK) {
        emit_error("EdsGetCameraList", error);
        return;
    }
    error = EdsGetChildCount(list, &count);
    if (error != EDS_ERR_OK) {
        EdsRelease(list);
        emit_error("EdsGetChildCount", error);
        return;
    }
    fprintf(stdout, "{\"ok\":true,\"cameras\":[");
    for (index = 0; index < count; index++) {
        EdsCameraRef camera = NULL;
        char product[256];
        int has_product = 0;
        if (EdsGetChildAtIndex(list, (EdsInt32)index, &camera) == EDS_ERR_OK) {
            has_product = read_string(camera, kEdsPropID_ProductName, product, sizeof(product));
        }
        if (index > 0) {
            putchar(',');
        }
        fprintf(stdout, "{\"index\":%u,\"product_name\":", (unsigned int)index);
        json_string(has_product ? product : NULL);
        putchar('}');
        if (camera != NULL) {
            EdsRelease(camera);
        }
    }
    fputs("]}\n", stdout);
    fflush(stdout);
    EdsRelease(list);
}

static void connect_camera(EdsInt32 requested_index) {
    EdsCameraListRef list = NULL;
    EdsUInt32 count = 0;
    EdsError error;
    close_camera();
    error = EdsGetCameraList(&list);
    if (error != EDS_ERR_OK) {
        emit_error("EdsGetCameraList", error);
        return;
    }
    error = EdsGetChildCount(list, &count);
    if (error != EDS_ERR_OK) {
        EdsRelease(list);
        emit_error("EdsGetChildCount", error);
        return;
    }
    if (requested_index < 0 || (EdsUInt32)requested_index >= count) {
        EdsRelease(list);
        emit_error("SelectCamera", EDS_ERR_NOT_SUPPORTED);
        return;
    }
    error = EdsGetChildAtIndex(list, requested_index, &g_camera);
    EdsRelease(list);
    if (error != EDS_ERR_OK) {
        g_camera = NULL;
        emit_error("EdsGetChildAtIndex", error);
        return;
    }
    activate_limited_properties(g_camera);
    error = EdsOpenSession(g_camera);
    if (error != EDS_ERR_OK) {
        EdsRelease(g_camera);
        g_camera = NULL;
        emit_error("EdsOpenSession", error);
        return;
    }
    g_session_open = 1;
    error = EdsSetPropertyEventHandler(
        g_camera,
        kEdsPropertyEvent_All,
        property_event_handler,
        NULL
    );
    if (error != EDS_ERR_OK) {
        close_camera();
        emit_error("EdsSetPropertyEventHandler", error);
        return;
    }
    error = pump_camera_events();
    if (error != EDS_ERR_OK) {
        close_camera();
        emit_error("EdsGetEvent(Connect)", error);
        return;
    }
    emit_camera_details(g_camera);
}

static void poll_camera(void) {
    char product[256];
    EdsError error;
    if (g_camera == NULL || !g_session_open) {
        emit_error("PollWithoutSession", EDS_ERR_NOT_SUPPORTED);
        return;
    }
    error = pump_camera_events();
    if (error != EDS_ERR_OK) {
        emit_error("EdsGetEvent(Poll)", error);
        return;
    }
    memset(product, 0, sizeof(product));
    error = EdsGetPropertyData(g_camera, kEdsPropID_ProductName, 0, sizeof(product), product);
    if (error != EDS_ERR_OK || product[0] == '\0') {
        emit_error("EdsGetPropertyData(ProductName)", error == EDS_ERR_OK ? EDS_ERR_NOT_SUPPORTED : error);
        return;
    }
    fputs("{\"ok\":true,\"product_name\":", stdout);
    json_string(product);
    fputs("}\n", stdout);
    fflush(stdout);
}

int main(int argc, char **argv) {
    char command[256];
    EdsError error;
    if (argc == 2 && strcmp(argv[1], "--enable-physical-writes") == 0) {
        g_physical_writes_enabled = 1;
    } else if (argc != 1) {
        fputs("{\"ok\":false,\"operation\":\"InvalidLaunchArguments\",\"code\":7}\n", stdout);
        fflush(stdout);
        return 2;
    }
    atexit(cleanup);
    error = EdsInitializeSDK();
    if (error != EDS_ERR_OK) {
        emit_error("EdsInitializeSDK", error);
        return 2;
    }
    g_sdk_initialized = 1;
    fputs("{\"ok\":true,\"event\":\"ready\"}\n", stdout);
    fflush(stdout);

    while (fgets(command, sizeof(command), stdin) != NULL) {
        size_t length = strlen(command);
        while (length > 0 && (command[length - 1] == '\n' || command[length - 1] == '\r')) {
            command[--length] = '\0';
        }
        if (strcmp(command, "DISCOVER") == 0) {
            discover_cameras();
        } else if (strncmp(command, "CONNECT ", 8) == 0) {
            char *end = NULL;
            long index = strtol(command + 8, &end, 10);
            if (end == command + 8 || *end != '\0' || index < 0) {
                emit_error("InvalidCameraIndex", EDS_ERR_NOT_SUPPORTED);
            } else {
                connect_camera((EdsInt32)index);
            }
        } else if (strcmp(command, "DETAILS") == 0) {
            if (g_camera == NULL || !g_session_open) {
                emit_error("DetailsWithoutSession", EDS_ERR_NOT_SUPPORTED);
            } else {
                emit_camera_details(g_camera);
            }
        } else if (strcmp(command, "POLL") == 0) {
            poll_camera();
        } else if (strcmp(command, "CAPABILITIES") == 0) {
            emit_capabilities();
        } else if (strncmp(command, "WRITE ", 6) == 0) {
            char key[64];
            unsigned long raw_value;
            char trailing;
            if (sscanf(command + 6, "%63s %lu %c", key, &raw_value, &trailing) != 2 || raw_value > 0xffffffffUL) {
                emit_error("InvalidWriteCommand", EDS_ERR_NOT_SUPPORTED);
            } else {
                write_qualified_candidate(key, (EdsUInt32)raw_value);
            }
        } else if (strcmp(command, "DISCONNECT") == 0) {
            close_camera();
            fputs("{\"ok\":true}\n", stdout);
            fflush(stdout);
        } else if (strcmp(command, "QUIT") == 0) {
            fputs("{\"ok\":true}\n", stdout);
            fflush(stdout);
            break;
        } else {
            emit_error("UnknownCommand", EDS_ERR_NOT_SUPPORTED);
        }
    }
    return 0;
}
