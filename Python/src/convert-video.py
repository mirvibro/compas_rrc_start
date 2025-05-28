import subprocess

def convert_codec(input_path, output_path):
    ffmpeg_path = r"C:\ProgramData\chocolatey\lib\ffmpeg-full\tools\ffmpeg\bin\ffmpeg.exe"

    command = [
        ffmpeg_path,
        '-i', input_path,
        '-vcodec', 'libx264',
        '-acodec', 'aac',
        '-strict', 'experimental',
        output_path
    ]
    subprocess.run(command)

#convert_codec('vids/2025-05-28_09-27-04.mp4', 'vids/2025-05-28_09-27-04-conv.mp4')