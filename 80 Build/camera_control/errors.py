"""Stable camera-control errors and command exit statuses."""


class CameraControlError(RuntimeError):
    exit_code = 5
    error_kind = "camera_control_error"

    def as_dict(self):
        return {
            "ok": False,
            "error": {
                "kind": self.error_kind,
                "message": str(self),
            },
        }


class SdkUnavailableError(CameraControlError):
    exit_code = 2
    error_kind = "sdk_unavailable"


class NoCameraError(CameraControlError):
    exit_code = 3
    error_kind = "no_camera"


class CameraSelectionError(CameraControlError):
    exit_code = 4
    error_kind = "camera_selection"

    def __init__(self, message, cameras=None):
        super().__init__(message)
        self.cameras = cameras or []

    def as_dict(self):
        result = super().as_dict()
        result["error"]["cameras"] = self.cameras
        return result


class WrongCameraModelError(CameraControlError):
    exit_code = 4
    error_kind = "wrong_camera_model"


class CameraSessionError(CameraControlError):
    exit_code = 5
    error_kind = "camera_session"


class CameraDisconnectedError(CameraControlError):
    exit_code = 5
    error_kind = "camera_disconnected"
