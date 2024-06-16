import csv

class Logger:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data = []

    def log(self, frame_id, detections):
        for detection in detections:
            bbox = detection[0].astype(int)
            row = [frame_id, "QR", bbox.tolist(), "N/A"]
            self.data.append(row)

    def save(self):
        with open(self.csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frame ID', 'QR id', 'QR 2D', 'QR 3D'])
            writer.writerows(self.data)
