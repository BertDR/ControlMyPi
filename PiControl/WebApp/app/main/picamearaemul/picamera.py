import collections
import shutil
import os

# VERY small emulation class for the PiCamera, used on systems where PiCamera cannot be installed
#   fi. Windows systems.

class PiCamera(object):
    resolution = collections.namedtuple('PiResolution', ('width', 'height'))

    def __enter__(self):
        return self
    def capture(self, output, format=None, use_video_port=False, resize=None,
            splitter_port=0, bayer=False, **options):
        base, filename = os.path.split(output)
#        base = os.path.basename(output)
        testfile=os.path.join(base, 'test.jpg')
        shutil.copyfile(testfile,output)
        return
    def __init__(
            self, camera_num=0, stereo_mode='none', stereo_decimate=False,
            resolution=None, framerate=None, sensor_mode=0, led_pin=None,
            clock_mode='reset', framerate_range=None):
        return
    def start_preview(self, **options):
        return
    def __exit__(self, exc_type, exc_value, exc_tb):
        return
