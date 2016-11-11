def play_audio(suffix):
    """
    Add to class instance methods: speak_sentence_to_SUFFIX and play_audio_file_to_SUFFIX
    which call play_audio_to_SUFFIX with right parameters
    """
    def add_methods(cl):
        def speak_sentence(self, id, sentence, gender='female', voice='susan', locale='en_US', tag=None):
            play_audio = getattr(self, 'play_audio_to_%s' % suffix)
            play_audio(id, {
                'sentence': sentence,
                'gender': gender,
                'voice': voice,
                'locale': locale,
                'tag': tag
            })

        def play_audio_file(self, id, file_url, tag=None):
            play_audio = getattr(self, 'play_audio_to_%s' % suffix)
            play_audio(id, {
                'fileUrl': file_url,
                'tag': tag
            })

        setattr(cl, 'speak_sentence_to_%s' % suffix, speak_sentence)
        setattr(cl, 'play_audio_file_to_%s' % suffix, play_audio_file)
        return cl
    return add_methods
