import cv2

class QRCodeDetector:
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def detect_qr(self, frame):
        _, points, _ = self.detector.detectAndDecodeMulti(frame)
        return points if points is not None else []

    def draw_detections(self, frame, detections):
        if detections is not None:
            for bbox in detections:
                bbox = bbox[0].astype(int)
                for i in range(len(bbox)):
                    cv2.line(frame, tuple(bbox[i]), tuple(bbox[(i + 1) % len(bbox)]), (0, 255, 0), 2)
                cv2.putText(frame, "QR", tuple(bbox[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame
