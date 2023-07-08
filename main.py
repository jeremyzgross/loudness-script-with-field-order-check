import os
import shutil
import ffmpeg
import pyloudnorm as pyln
import soundfile as sf
import moviepy.editor as mp

BASE_PATH = '/Users/jeremyzgross/Downloads/BLACKSPOT QC/'

def measure_loudness():
    badframerateCounter = 0

    for filename in os.listdir(BASE_PATH + 'TEST VIDEOS'):
        if not filename.endswith((".mov", ".mp4", '.mxf')):
            continue
        print(filename)

        sourceMp4Path = os.path.join(BASE_PATH, 'TEST VIDEOS', filename)
        probe = ffmpeg.probe(sourceMp4Path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            continue

        frame_rate = video_stream.get('r_frame_rate')
        field_order = video_stream.get('field_order')
        print(f'Frame rate: {frame_rate}')
        print(f'Field order: {field_order}')
        if frame_rate == '24000/1001' and field_order == 'progressive':
            shutil.move(sourceMp4Path, os.path.join(BASE_PATH, 'GOOD VIDEOS'))
        elif frame_rate == '30000/1001' and field_order == 'tb':
            shutil.move(sourceMp4Path, os.path.join(BASE_PATH, 'GOOD VIDEOS'))
        else:
            shutil.move(sourceMp4Path, os.path.join(BASE_PATH, 'BAD VIDEOS'))
            badframerateCounter += 1

    for filename in os.listdir(os.path.join(BASE_PATH, 'GOOD VIDEOS')):
        if not filename.endswith((".mov", ".mp4", ".mxf")):
            continue
        clip = mp.VideoFileClip(os.path.join(BASE_PATH, 'GOOD VIDEOS', filename))
        noext = os.path.splitext(filename)[0]
        print(f'noext {noext}')
        print(f'writing file')
        clip.audio.write_audiofile(os.path.join(BASE_PATH, 'EXPORTED MP3s', f'{noext}.mp3'))

    loud_files = 0
    for filename in os.listdir(os.path.join(BASE_PATH, 'EXPORTED MP3s')):
        if not filename.endswith(".mp3"):
            continue
        data, rate = sf.read(os.path.join(BASE_PATH, 'EXPORTED MP3s', filename))
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(data)
        sourceMovPath = os.path.join(BASE_PATH, 'GOOD VIDEOS', os.path.splitext(filename)[0] + '.mov')
        if loudness >= -22 or loudness <= -26:
            shutil.move(sourceMovPath, os.path.join(BASE_PATH, 'BAD VIDEOS'))
            loud_files += 1
        else:
            print(f'{filename} does not need to be moved.')

        print(filename)
        print('loudness')
        print(loudness)

    print(str(loud_files) + " LOUD FILES")
    print(f'Number of videos with bad frame rate and/or field order: {badframerateCounter}')

    # Clear files in the MP3 folder
    mp3Folder = os.path.join(BASE_PATH, 'EXPORTED MP3s')
    for filename in os.listdir(mp3Folder):
        file_path = os.path.join(mp3Folder, filename)
        try:
            if filename.endswith(".mp3"):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    # # Move files back into TEST VIDEO folder for testing
    # Good_videos_source = os.path.join(BASE_PATH, 'GOOD VIDEOS')
    # Bad_videos_source = os.path.join(BASE_PATH, 'BAD VIDEOS')
    # original_videos = os.path.join(BASE_PATH, 'TEST VIDEOS')
    #
    # allgoodfiles = os.listdir(Good_videos_source)
    # allbadfiles = os.listdir(Bad_videos_source)
    #
    # for f in allgoodfiles:
    #     src_path = os.path.join(Good_videos_source, f)
    #     dst_path = os.path.join(original_videos, f)
    #     shutil.move(src_path, dst_path)
    #
    # for f in allbadfiles:
    #     src_path_2 = os.path.join(Bad_videos_source, f)
    #     dst_path = os.path.join(original_videos, f)
    #     shutil.move(src_path_2, dst_path)


if __name__ == '__main__':
    measure_loudness()
