from pydub import AudioSegment
from pydub.playback import play

song = AudioSegment.from_mp3("kalank.mp3")
song = song[:60000]
start = 1000
end = 10000
silent = song.silent(end-start)
song = song.overlay(silent,position=start,gain_during_overlay=-20)
# song.silent(10000)
play(song)
file_handle = song.export("output.mp3", format="mp3")