from threading import Thread, Lock
import pyautogui as auto
import pyaudio as audio
import argparse
import time
from Sections.APIS.FFT.src.stream_analyzer import Stream_Analyzer

class Bot:

    sr = 16000
    chunk = 1 * sr
    channel_nr = 1
    ear = None
    audio_interface = audio.PyAudio()
    audio_stream = audio_interface.open(format=audio.paInt16,
                                        channels=channel_nr,
                                        rate=sr,
                                        input=True,
                                        frames_per_buffer=chunk)

    

    # Constructor to start thread lock
    def __init__(self):
        # Creates a thread and locks it
        self.lock = Lock()

    # Thread properties
    stopped = True
    lock = None
    points = None

    def update_points(self, points):
        self.lock.acquire()
        self.points = points
        self.lock.release()

    def start(self):
        self.stopped = False
        a = Thread(target=self.audio_visualizer)
        a.start()
        time.sleep(25)
        t = Thread(target=self.run)
        t.start()

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--device', type=int, default=None, dest='device',
                            help='pyaudio (portaudio) device index')
        parser.add_argument('--height', type=int, default=450, dest='height',
                            help='height, in pixels, of the visualizer window')
        parser.add_argument('--n_frequency_bins', type=int, default=400, dest='frequency_bins',
                            help='The FFT features are grouped in bins')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--window_ratio', default='24/9', dest='window_ratio',
                            help='float ratio of the visualizer window. e.g. 24/9')
        parser.add_argument('--sleep_between_frames', dest='sleep_between_frames', action='store_true',
                            help='when true process sleeps between frames to reduce CPU usage (recommended for low update rates)')
        return parser.parse_args()


    def audio_visualizer(self):
        args = self.parse_args()
        window_ratio = ( 16 / 9 )
        self.ear = Stream_Analyzer(
                    device = 1,        # Pyaudio (portaudio) device index, defaults to first mic input
                    rate   = None,               # Audio samplerate, None uses the default source settings
                    FFT_window_size_ms  = 60,    # Window size used for the FFT transform
                    updates_per_second  = 1000,  # How often to read the audio stream for new data
                    smoothing_length_ms = 50,    # Apply some temporal smoothing to reduce noisy features
                    n_frequency_bins = args.frequency_bins, # The FFT features are grouped in bins
                    visualize = 1,               # Visualize the FFT features with PyGame
                    verbose   = args.verbose,    # Print running statistics (latency, fps, ...)
                    height    = 200,     # Height, in pixels, of the visualizer window,
                    window_ratio = window_ratio  # Float ratio of the visualizer window. e.g. 24/9
                    )
        fps = 60  #How often to update the FFT features + display
        last_update = time.time()
        while True:
            if (time.time() - last_update) > (1./fps):
                last_update = time.time()
                raw_fftx, raw_fft, binned_fftx, binned_fft = self.ear.get_audio_features()
            elif args.sleep_between_frames:
                time.sleep(((1./fps)-(time.time()-last_update)) * 0.99)


    # Stops this thread.
    def stop(self):
        self.stopped = True

    # Our loop function for this thread.
    def run(self):
        while not self.stopped:
            if not self.points is None:
                points = self.points
                one = None
                two = None
                if not self.ear is None:
                    if len(points) > 0:
                         one = points[0]
                         if len(points) > 1:
                             two = points[1]
                    auto.mouseDown(one, button = 'right')
                    if round(self.ear.strongest_frequency) > 60:
                        auto.click(button = 'left')
                    if two is not None:
                        while auto.moveTo(two, duration = 0.05):
                            auto.click(button = 'left')
                    auto.mouseUp(button = 'right')