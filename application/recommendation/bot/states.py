from abc import ABC, abstractmethod
from recommendation import models, facebook, sentiment, neural_network
from recommendation.bot import quick_replies as qr
import json


class State(ABC):

    user_response = None
    name = None
    next_state = None
    new_profile = False

    def __init__(self, user_id):
        self.user_infos = facebook.get_user_infos(user_id)
        self.user_id = user_id

    @abstractmethod
    def get_text(self):
        pass

    def next(self):
        user_state = models.UserState.objects.get(user=self.user_id)
        user_state.state = self.next_state
        user_state.save()

    def set_profile(self):
        self.user_profile = models.UserProfile.objects.get_or_create(
            user=self.user_id,
        )[0]
        if self.new_profile:
            self.user_profile.is_student = 0
            self.user_profile.documents_sheets = 0
            self.user_profile.image_video = 0
            self.user_profile.performance = 0
            self.user_profile.heavy_games = 0
            self.user_profile.light_games = 0
            self.user_profile.cost_benefit = 0
            self.user_profile.save()

    def handle_message(self, message):
        quick_reply = message['message'].get('quick_reply', None)
        if quick_reply:
            self.handle_quick_reply(quick_reply)
        else:
            self.handle_text(message['message']['text'])

    def handle_text(self, text):
        self.user_response = sentiment.classify(text)

    def handle_quick_reply(self, quick_reply):
        self.user_response = True
        reply_data = json.loads(quick_reply['payload'])
        if 'attribute' in reply_data.keys():
            setattr(self.user_profile,
                    reply_data['attribute'],
                    reply_data['value'])
            self.user_profile.save()

    def get_quick_replies(self):
        return None

    def get_attachment(self):
        return None


class WelcomeState(State):
    name = 'welcome'
    next_state = 'student'
    new_profile = True

    def get_text(self):
        return ("Olá, {}! Tudo bem? Eu posso te ajudar a escolher um "
                "notebook ideal pra você! Basta responder algumas perguntas "
                "e eu farei uma análise do seu perfil e direi o melhor "
                "notebook para você! Vamos começar?".format(
                    self.user_infos['first_name']
                ))


class StudentState(State):
    name = 'student'
    next_state = 'student'

    def handle_message(self, message):
        super(StudentState, self).handle_message(message)
        if self.user_response is not None:
            if self.user_response == 'pos':
                self.next_state = 'work'
            else:
                self.next_state = 'welcome'

    def get_text(self):
        if self.user_response is None:
            text = ('Desculpe, não consegui te entender...\r\nVamos começar?')
        elif self.user_response == 'pos':
            text = ('Ótimo!\r\nVamos para a primeira pergunta!\r\n\r\n'
                    'Você é estudante?')
        else:
            text = ('Ah, tudo bem, fica pra próxima :(\r\n\r\n'
                    'Volte quando tiver mais tempo!')
        return text


class WorkState(State):
    name = 'work'
    next_state = 'work'

    def handle_message(self, message):
        super(WorkState, self).handle_message(message)
        if self.user_response is not None:
            if self.user_response == 'pos':
                self.user_profile.is_student = 1
                self.user_profile.save()

            self.next_state = 'wait_work'

    def get_text(self):
        if self.user_response is None:
            text = ('Desculpe, não consegui te entender...\r\nÉ estudante?')
        else:
            text = ('Anotado!\r\n\r\nPodemos ir para a próxima pergunta:\r\n'
                    'Você pretende user o notebook para trabalhar?')
        return text

    def get_quick_replies(self):
        if self.user_response:
            replies = [
                reply
                for key, reply in qr.work_replies.items()
            ]

            replies.insert(0, qr.stop('Para trabalho não'))
            return replies
        else:
            return None


class WaitWorkState(State):
    name = 'wait_work'
    next_state = 'wait_work'
    move_to_next = False

    def handle_quick_reply(self, quick_reply):
        super(WaitWorkState, self).handle_quick_reply(quick_reply)
        reply_data = json.loads(quick_reply['payload'])
        if 'stop' in reply_data.keys():
            self.next_state = 'wait_game'
            self.move_to_next = True

    def get_text(self):
        if self.user_response and not self.move_to_next:
            text = ('Você está procurando um notebook para mais algum tipo '
                    'de trabalho?')
        elif self.move_to_next:
            text = ('Obrigado! :)\r\n\r\nVocê pretende usar o notebook para '
                    'jogar?')
        else:
            text = ('Desculpe, mas você poderia escolher uma das opções?')

        return text

    def get_quick_replies(self):
        if not self.move_to_next:
            replies = []
            for attribute, attribute_reply in qr.work_replies.items():
                if not getattr(self.user_profile, attribute):
                    replies.append(attribute_reply)

            replies.insert(0, qr.stop('Não'))
            return replies
        else:
            replies = [
                reply
                for key, reply in qr.game_replies.items()
            ]

            replies.insert(0, qr.stop('Nada de jogo'))
            return replies


class WaitGameState(State):
    name = 'wait_game'
    next_state = 'wait_game'
    move_to_next = False

    def handle_quick_reply(self, quick_reply):
        super(WaitGameState, self).handle_quick_reply(quick_reply)
        reply_data = json.loads(quick_reply['payload'])
        if 'stop' in reply_data.keys():
            self.next_state = 'suggest'
            self.move_to_next = True

    def get_text(self):
        if self.user_response and not self.move_to_next:
            text = ('Você pretende jogar o outro tipo de jogo também?')
        elif self.move_to_next:
            text = ('Obrigado pela resposta :)\r\n\r\n'
                    'Última pergunta, prometo! Você prefere um notebook '
                    'que atenda muito bem ao seu perfil ou um que atenda '
                    'minimamente?')
        else:
            text = ('Desculpe, mas você poderia escolher uma das opções?')

        return text

    def get_quick_replies(self):
        if not self.move_to_next:
            replies = []
            for attribute, attribute_reply in qr.game_replies.items():
                if not getattr(self.user_profile, attribute):
                    replies.append(attribute_reply)

            replies.insert(0, qr.stop('Não'))
            return replies
        else:
            replies = [
                reply
                for key, reply in qr.cost_replies.items()
            ]
            return replies


class SuggestState(State):
    name = 'suggest'
    next_state = 'suggest'

    def handle_quick_reply(self, quick_reply):
        super(SuggestState, self).handle_quick_reply(quick_reply)
        reply_data = json.loads(quick_reply['payload'])
        if 'attribute' in reply_data.keys():
            self.next_state = 'welcome'

    def get_text(self):
        if self.user_response:
            return None
        else:
            return ('Desculpe, mas você poderia escolher uma das opções?')

    def get_quick_replies(self):
        if self.user_response:
            return None
        else:
            replies = [
                reply
                for key, reply in qr.cost_replies.items()
            ]
            return replies

    def get_attachment(self):
        classifier = neural_network.Classifier()
        profile = {
            field.name: 1
            for field in self.user_profile._meta.fields
            if getattr(self.user_profile, field.name) == 1
        }
        notebooks = classifier.suggest(**profile)

        elements = []
        for notebook in notebooks:
            element = {
                'title': notebook.name,
                'subtitle': ('R$%0.2f' % notebook.price),
                'image_url': notebook.thumbnail,
                'buttons': [
                    {'title': 'Comprar',
                     'type': 'web_url',
                     'url': notebook.link},
                ]
            }
            elements.append(element)

        return {
            'type': 'template',
            'payload': {
                'template_type': 'list',
                'top_element_style': 'large',
                'elements': elements
            }
        }


class StateHandler:

    states = {
        'welcome': WelcomeState,
        'student': StudentState,
        'work': WorkState,
        'wait_work': WaitWorkState,
        'wait_game': WaitGameState,
        'suggest': SuggestState,
    }

    def __init__(self, state, user_id):
        self._state = self.states[state](user_id)

    def process_message(self, message):
        self._state.set_profile()
        self._state.handle_message(message)
        response = {
            'text': self._state.get_text(),
            'attachment': self._state.get_attachment(),
            'quick_replies': self._state.get_quick_replies(),
        }
        self._state.next()
        return response
