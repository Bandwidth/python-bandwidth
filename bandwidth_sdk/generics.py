from .utils import to_api


class AudioMixin(object):
    client = None

    def play_audio(self, file_url, **kwargs):
        """
        Plays audio form the given url to the call associated with call_id

        :param file_url: The location of an audio file to play (WAV and MP3 supported).

        :param loop_enabled: When value is true, the audio will keep playing in a loop. Default: false.

        :param tag:	A string that will be included in the events delivered when the audio playback starts or finishes.

        :return: None
        """

        url = self.get_audio_url()
        kwargs['file_url'] = file_url
        data = to_api(kwargs)
        self.client.post(url, data=data)

    def stop_audio(self):
        """
        Stop an audio file playing
        """
        url = self.get_audio_url()
        self.client.post(url, data=to_api({'file_url': ''}))

    def speak_sentence(self, sentence, **kwargs):
        """
        :param sentence: The sentence to speak.

        :param gender: The gender of the voice used to synthesize the sentence. It will be considered only if sentence
                    is not null. The female gender will be used by default.

        :param locale: The locale used to get the accent of the voice used to synthesize the sentence. Currently
            Bandwidth API supports:

            en_US or en_UK (English)
            es or es_MX (Spanish)
            fr or fr_FR (French)
            de or de_DE (German)
            it or it_IT (Italian)

            It will be considered only if sentence is not null/empty. The en_US will be used by default.
        :param voice: The voice to speak the sentence. The API currently supports the following voices:

            English US: Kate, Susan, Julie, Dave, Paul
            English UK: Bridget
            Spanish: Esperanza, Violeta, Jorge
            French: Jolie, Bernard
            German: Katrin, Stefan
            Italian: Paola, Luca

            It will be considered only if sentence is not null/empty. Susan's voice will be used by default.

        :param loop_enabled: When value is true, the audio will keep playing in a loop. Default: false.

        :param tag:	A string that will be included in the events delivered when the audio playback starts or finishes.

        :return: None
        """
        url = self.get_audio_url()
        kwargs['sentence'] = sentence
        data = to_api(kwargs)
        self.client.post(url, data=data)

    def stop_sentence(self):
        """
        Stop a current sentence
        :return: None
        """
        url = self.get_audio_url()
        self.client.post(url, data=to_api({'sentence': ''}))

    def get_audio_url(self):
        raise NotImplementedError  # pragma: no cover
