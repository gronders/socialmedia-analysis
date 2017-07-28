class Tone():
   
    def __init__(self,tone_name, score, tone_id):
        self.tone_name = tone_name
        self.score = score
        self.tone_id = tone_id

class ToneCategory():
    def __init__(self, category_id, toneArray, category_name):
        self.category_id = category_id
        self.tones = toneArray
        self.category_name = category_name

