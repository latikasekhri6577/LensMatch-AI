import math
import cv2

def is_blurry(image, threshold=100.0):
    """Returns True if the image appears blurry, based on Laplacian variance."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold

def horizontal_distance(p1, p2, w):
    return abs((p2.x * w) - (p1.x * w))


def vertical_distance(p1, p2, h):
    return abs((p2.y * h) - (p1.y * h))


def euclidean_distance(p1, p2, w, h):
    x1, y1 = p1.x * w, p1.y * h
    x2, y2 = p2.x * w, p2.y * h
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def calculate_angle(p1, vertex, p2, w, h):
    """Angle at 'vertex' formed by rays to p1 and p2, in degrees."""
    a = (p1.x * w - vertex.x * w, p1.y * h - vertex.y * h)
    b = (p2.x * w - vertex.x * w, p2.y * h - vertex.y * h)

    dot = a[0] * b[0] + a[1] * b[1]
    mag_a = math.hypot(*a)
    mag_b = math.hypot(*b)

    cos_angle = dot / (mag_a * mag_b)
    cos_angle = max(-1.0, min(1.0, cos_angle))  # clamp for float safety
    return math.degrees(math.acos(cos_angle))


def calculate_measurements(face_landmarks, w, h):

    lm = face_landmarks.landmark

    # ---- Existing measurements (unchanged) ----
    face_width = horizontal_distance(lm[234], lm[454], w)
    face_height = vertical_distance(lm[10], lm[152], h)
    forehead_width = horizontal_distance(lm[70], lm[300], w)
    cheekbone_width = horizontal_distance(lm[116], lm[345], w)
    jaw_width = horizontal_distance(lm[172], lm[397], w)

    aspect_ratio = face_height / face_width

    # ---- NEW: chin-to-jaw ratio (pointed vs rounded chin) ----
    chin_width = horizontal_distance(lm[176], lm[400], w)
    chin_to_jaw_ratio = chin_width / jaw_width

    # ---- NEW: jaw angle (sharp V vs wide/flat jaw) ----
    jaw_angle = calculate_angle(lm[172], lm[152], lm[397], w, h)

    # ---- NEW: jowl taper (how fast face narrows cheek -> jaw) ----
    jowl_width = horizontal_distance(lm[58], lm[288], w)
    jowl_taper_ratio = jowl_width / cheekbone_width

    return {
        "face_width": face_width,
        "face_height": face_height,
        "forehead_width": forehead_width,
        "cheekbone_width": cheekbone_width,
        "jaw_width": jaw_width,

        "aspect_ratio": aspect_ratio,
        "forehead_ratio": forehead_width / face_width,
        "cheek_ratio": cheekbone_width / face_width,
        "jaw_ratio": jaw_width / face_width,

        # New shape-sensitive features
        "chin_to_jaw_ratio": chin_to_jaw_ratio,
        "jaw_angle": jaw_angle,
        "jowl_taper_ratio": jowl_taper_ratio,
    }