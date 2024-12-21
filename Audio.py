from pygame import mixer as mx

mx.init()

class music():
    def __init__(self) -> None:
        pass

    def play(song: str, Volume : float) -> None:
        mx.music.load(f"Assets/Music/{song}.wav")
        mx.music.play(-1)
        mx.music.set_volume(Volume)

Death = mx.Sound("Assets/Music/Death.wav")