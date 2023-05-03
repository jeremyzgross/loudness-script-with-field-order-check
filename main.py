import os
import shutil
import ffmpeg
import pyloudnorm as pyln
import soundfile as sf
import moviepy.editor as mp
# setting a field that points to ffmpeg (a library)
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"

BASE_PATH = '/Users/jeremyzgross/Downloads/BLACKSPOT QC/'

# converts video files to sound only files (mp3s)
def measure_loudness():
    badframerateCounter = 0

    # for loop that loops through a directory in your OS. Replace the directory in the () to where your video files are located.
    for filename in os.listdir(BASE_PATH + 'TEST VIDEOS'):
        if not filename.endswith(".mp4") and not filename.endswith(".mov"):
            continue

        print(filename)  # prints which file is being processed

        sourceMp4Path = '/Users/jeremyzgross/Downloads/BLACKSPOT QC/TEST VIDEOS/' + os.path.splitext(filename)[
            0] + '.mov'

        # use ffmpeg to probe the video file and extract metadata
        probe = ffmpeg.probe(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/TEST VIDEOS/{filename}')
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            continue  # skip files without video stream

        frame_rate = video_stream.get('r_frame_rate')
        field_order = video_stream.get('field_order')
        print(f'Frame rate: {frame_rate}')
        print(f'Field order: {field_order}')
        if frame_rate == '24000/1001' and field_order == 'progressive':
            shutil.move(sourceMp4Path, f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS')
        elif frame_rate == '30000/1001' and field_order == 'tb':
            shutil.move(sourceMp4Path, f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS')
        else:
            shutil.move(sourceMp4Path, f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/BAD VIDEOS')
            badframerateCounter += 1

 # uses moviepy to load video file into 'clip' varaible. Replace the directory in the () to where your video files are locate bewtween f and {filename}. Make sure there is a / at the end of your directory
    for filename in os.listdir(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS'):
        if not filename.endswith(".mp4") and not filename.endswith(".mov"):
            continue
        clip = mp.VideoFileClip(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS/{filename}')
        # removes extension from file name before converting
        noext = os.path.splitext(filename)[0]
        print(f'noext {noext}')
        print(f'writing file')
        # creates mp3 file. Replace the directory with where the converted video to audio file will be placed bewtween F and {noext}
        clip.audio.write_audiofile(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/EXPORTED MP3s/{noext}.mp3')

    # for loop that measures loudness.  Replace the directory with where the converted video to audio file are placed
    loud_files = 0
    for filename in os.listdir(f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/EXPORTED MP3s'):
        if not filename.endswith(".mp3"):  # specifies that it is looking for mp3 files
            continue
        data, rate = sf.read(
            f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/EXPORTED MP3s/{filename}')  # load audio (with shape (samples, channels)). Replace the directory in the () to where your audio files are located bewtween f and {filename}. Make sure there is a / at the end of your directory
        meter = pyln.Meter(rate)  # create BS.1770 meter
        loudness = meter.integrated_loudness(data)  # measure loudness
        sourceMp4Path = '/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS/' + os.path.splitext(filename)[
            0] +'.mov'
        if loudness >= -22 and loudness <= -26:
            # move mov to a folder GOOD
            shutil.move(sourceMp4Path, f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/BAD VIDEOS')
            badCounter += 1

        else:
            print(f'{filename} does not need to be moved.')

        print(filename)
        print('loudness')
        print(loudness)
    print(str(loud_files) + " LOUD FILES")
    print(f'Number of videos with bad frame rate and/or field order: {badframerateCounter}')

    # clears files in MP3 folder
    mp3Folder = f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/EXPORTED MP3s'
    for filename in os.listdir(mp3Folder):
        file_path = os.path.join(mp3Folder, filename)
        try:
            # if the filename is a file, delete it
            if filename.endswith(".mp3"):
                os.unlink(file_path)
            # if the filename is a dir, delete the dir
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

# # moves files back into TEST VIDEO folder for testing. Uncomment below when needed
#
#     Good_videos_source = f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/GOOD VIDEOS/'
#     Bad_videos_source= f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/BAD VIDEOS/'
#     orginal_videos = f'/Users/jeremyzgross/Downloads/BLACKSPOT QC/TEST VIDEOS/'
#     # gather all files
#     allgoodfiles = os.listdir(Good_videos_source)
#     allbadfiles = os.listdir(Bad_videos_source)
#
#     # iterate on all files to move them to destination folder
#     for f in allgoodfiles:
#         src_path = os.path.join(Good_videos_source, f)
#         dst_path = os.path.join(orginal_videos, f)
#         shutil.move(src_path, dst_path)
#
#     for f in allbadfiles:
#         src_path_2 = os.path.join(Bad_videos_source, f)
#         dst_path = os.path.join(orginal_videos, f)
#         shutil.move(src_path_2, dst_path)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    measure_loudness()


