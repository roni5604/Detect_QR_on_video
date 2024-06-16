import os
import tkinter as tk
from tkinter import ttk
from video_processor import VideoProcessor

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    video_path = os.path.join(base_dir, "TestVideos", "classVideo.mp4")
    output_video_path = os.path.join(base_dir, "Output", "output_video.mp4")
    csv_path = os.path.join(base_dir, "Output", "output_data.csv")

    processor = VideoProcessor(video_path, output_video_path, csv_path)

    def start_pause_video():
        if not processor.started:
            processor.start_processing()
            start_pause_button.config(text="Pause")
        else:
            processor.toggle_pause()
            start_pause_button.config(text="Start" if processor.paused else "Pause")

    root = tk.Tk()
    root.title("Video Processor")

    start_pause_button = ttk.Button(root, text="Start", command=start_pause_video)
    start_pause_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
