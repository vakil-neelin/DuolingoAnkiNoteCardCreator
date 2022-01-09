class Word(object):

    def __init__(self, normalized_word, word_string,
                 skill, audio_file, image_file, translation=""):
        self._normalized_word = normalized_word
        self._word_string = word_string
        self._skill = skill

        audio_file = audio_file.strip()
        audio_file = audio_file.replace(" ", "_")
        self._audio_file = audio_file

        image_file = image_file.strip()
        image_file = image_file.replace(" ", "_")
        self._image_file = image_file
        self._translation = translation
        return

    def __str__(self):
        temp = "Normalized Word: " + str(self._normalized_word) + "\n"
        temp += "Word: " + str(self._word_string) + "\n"
        temp += "Skill: " + str(self._skill) + "\n"
        temp += "Audio File: " + str(self._audio_file) + "\n"
        temp += "Translation: " + str(self._translation) + "\n"
        return temp

    @property
    def normalized_word(self):
        return self._normalized_word

    @normalized_word.setter
    def normalized_word(self, value):
        self._normalized_word = value
        return

    @property
    def word_string(self):
        return self._word_string

    @word_string.setter
    def word_string(self, value):
        self._word_string = value
        return

    @property
    def skill(self):
        return self._skill

    @skill.setter
    def skill(self, value):
        self._skill = value
        return

    @property
    def audio_file(self):
        return self._audio_file

    @audio_file.setter
    def audio_file(self, value):
        value = value.strip()
        value = value.replace(" ", "_")
        self._audio_file = value
        return

    @property
    def image_file(self):
        return self._image_file

    @image_file.setter
    def image_file(self, value):
        value = value.strip()
        value = value.replace(" ", "_")
        self._image_file = value
        return

    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, value):
        self._translation = value
        return

    def __eq__(self, other):
        return self.word_string == other.word_string and \
               self.skill == other.skill
