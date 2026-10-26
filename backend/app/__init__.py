import os

# On macOS, OpenCV cannot show the camera-permission prompt from a background
# thread. With this set, the permission belongs to the app that launched the
# backend (Terminal, iTerm or VS Code), which macOS asks about instead.
os.environ.setdefault("OPENCV_AVFOUNDATION_SKIP_AUTH", "1")
