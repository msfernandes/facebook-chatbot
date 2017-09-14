from abc import ABC, abstractmethod
from recommendation import models, facebook, sentiment, neural_network
import json


class State(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def next(self, user_id):
        pass

    @abstractmethod
    def text(self, user_infos):
        pass

    @abstractmethod
    def handle_message(self, message):
        pass

    def quick_replies(self, user_infos):
        return None

    def attachment(self, user_infos):
        return None


class PriceState(State):
    name = 'price'

    def __init__(self):
        self.user_response = None
        self.next_state = 'price'

    def handle_message(self, message):
        quick_reply = message['message'].get('quick_reply', None)
        self.user_profile = models.UserProfile.objects.get_or_create(
            user=message['sender']['id']
        )[0]
        if quick_reply:
            reply_data = json.loads(quick_reply['payload'])
            if 'attribute' in reply_data.keys():
                setattr(self.user_profile,
                        reply_data['attribute'],
                        reply_data['value'])
                self.user_profile.save()
                self.next_state = 'welcome'
            self.user_response = True

    def text(self, user_infos):
        if self.user_response:
            return None
        else:
            return ('Desculpe, mas você poderia escolher uma das opções?')

    def next(self, user_id):
        user_state = models.UserState.objects.get(user=user_id)
        user_state.state = self.next_state
        user_state.save()

    def quick_replies(self, user_infos):
        if self.user_response:
            return None
        else:
            return [
                {'content_type': 'text',
                 'title': 'O melhor possível',
                 'image_url': ('https://maxcdn.icons8.com/Share/icon/Finance/'
                               'money_bag_filled1600.png'),
                 'payload': '{"attribute": "cost_benefit", "value": 0}'},
                {'content_type': 'text',
                 'title': 'O suficiente',
                 'image_url': ('https://d30y9cdsu7xlg0.cloudfront.net/png/'
                               '48167-200.png'),
                 'payload': '{"attribute": "cost_benefit", "value": 1}'},
            ]

    def attachment(self, user_infos):
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


class WhichGamesState(State):
    name = 'which_games'

    replies = {
        'heavy_games': {
            'content_type': 'text',
            'title': 'De Witcher 3 pra cima',
            'image_url': ('https://orig05.deviantart.net/3e0e/f/2015/1'
                          '37/8/5/the_witcher_3__wild_hunt___icon_by_'
                          'blagoicons-d8tt0rh.png'),
            'payload': '{"attribute": "heavy_games", "value": 1}'
        },
        'light_games': {
            'content_type': 'text',
            'title': 'Só um Diablo II mesmo',
            'image_url': ('http://2.bp.blogspot.com/_phtIMdxamd0/'
                          'TQtyT4p2VMI/AAAAAAAAAII/cYZHBMokYHc/s1600/'
                          'Diablo+II+new+1.png'),
            'payload': '{"attribute": "light_games", "value": 1}'},
    }

    def __init__(self):
        self.user_response = None
        self.next_state = 'which_games'
        self.move_to_nex = False

    def handle_message(self, message):
        quick_reply = message['message'].get('quick_reply', None)
        self.user_profile = models.UserProfile.objects.get_or_create(
            user=message['sender']['id']
        )[0]
        if quick_reply:
            reply_data = json.loads(quick_reply['payload'])
            if 'attribute' in reply_data.keys():
                setattr(self.user_profile,
                        reply_data['attribute'],
                        reply_data['value'])
                self.user_profile.save()
            else:
                self.next_state = 'price'
                self.move_to_nex = True
            self.user_response = True

    def text(self, user_infos):
        if self.user_response and not self.move_to_nex:
            return ('Você pretende jogar o outro tipo de jogo também?')
        elif self.move_to_nex:
            return ('Obrigado pela resposta :)\r\n'
                    'Última pergunta, prometo! Você prefere um notebook '
                    'que atenda muito bem ao seu perfil ou um que atenda '
                    'minimamente?')
        else:
            return ('Desculpe, mas você poderia escolher uma das opções?')

    def quick_replies(self, user_infos):
        if not self.move_to_nex:
            replies = []
            for attribute, attribute_reply in self.replies.items():
                if not getattr(self.user_profile, attribute):
                    replies.append(attribute_reply)

            replies.append({
                'content_type': 'text',
                'title': 'Pronto',
                'image_url': ('https://d30y9cdsu7xlg0.cloudfront.net/'
                              'png/161138-200.png'),
                'payload': '{"stop": true}'
            })
            return replies
        else:
            return [
                {'content_type': 'text',
                 'title': 'O melhor possível',
                 'image_url': ('https://maxcdn.icons8.com/Share/icon/Finance/'
                               'money_bag_filled1600.png'),
                 'payload': '{"attribute": "cost_benefit", "value": 0}'},
                {'content_type': 'text',
                 'title': 'O suficiente',
                 'image_url': ('https://d30y9cdsu7xlg0.cloudfront.net/png/'
                               '48167-200.png'),
                 'payload': '{"attribute": "cost_benefit", "value": 1}'},
            ]

    def next(self, user_id):
        user_state = models.UserState.objects.get(user=user_id)
        user_state.state = self.next_state
        user_state.save()


class WhichWorksState(State):
    name = 'which_works'

    replies = {
        'documents_sheets': {
            'content_type': 'text',
            'title': 'Pacote Office',
            'image_url': ('https://icon-icons.com/icons2/908/PNG/512/'
                          'pencil-and-two-white-sheets-of-paper_icon-'
                          'icons.com_70650.png'),
            'payload': '{"attribute": "documents_sheets", "value": 1}'
        },
        'image_video': {
            'content_type': 'text',
            'title': 'Edição de fotos/vídeos',
            'image_url': ('https://d30y9cdsu7xlg0.cloudfront.net/'
                          'png/16203-200.png'),
            'payload': '{"attribute": "image_video", "value": 1}'
        },
        'performance': {
            'content_type': 'text',
            'title': 'Alta performance',
            'image_url': ('https://d30y9cdsu7xlg0.cloudfront.net/'
                          'png/366778-200.png'),
            'payload': '{"attribute": "performance", "value": 1}'
        }
    }

    def __init__(self):
        self.user_response = None
        self.next_state = 'which_works'
        self.move_to_nex = False

    def handle_message(self, message):
        quick_reply = message['message'].get('quick_reply', None)
        self.user_profile = models.UserProfile.objects.get_or_create(
            user=message['sender']['id']
        )[0]
        if quick_reply:
            reply_data = json.loads(quick_reply['payload'])
            if 'attribute' in reply_data.keys():
                setattr(self.user_profile,
                        reply_data['attribute'],
                        reply_data['value'])
                self.user_profile.save()
            else:
                self.next_state = 'which_games'
                self.move_to_nex = True
            self.user_response = True

    def text(self, user_infos):
        if self.user_response and not self.move_to_nex:
            return ('Você está procurando um computador para mais algum '
                    'tipo de trabalho?')
        elif self.move_to_nex:
            return ('Obrigado pela resposta! :)\r\nVocê pretende usar o  '
                    'notebook para jogar?')
        else:
            return ('Desculpe, mas você poderia escolher uma das opções?')

    def quick_replies(self, user_infos):
        if not self.move_to_nex:
            replies = []
            for attribute, attribute_reply in self.replies.items():
                if not getattr(self.user_profile, attribute):
                    replies.append(attribute_reply)

            replies.append({
                'content_type': 'text',
                'title': 'Pronto',
                'image_url': ('https://d30y9cdsu7xlg0.cloudfront.net/'
                              'png/161138-200.png'),
                'payload': '{"stop": true}'
            })
            return replies
        else:
            return [
                {'content_type': 'text',
                 'title': 'Nada de jogo',
                 'image_url': ('http://wfarm2.dataknet.com/static/'
                               'resources/icons/set21/3d6cfa22dd6.png'),
                 'payload': '{"stop": true}'},
                {'content_type': 'text',
                 'title': 'De Witcher 3 pra cima',
                 'image_url': ('https://orig05.deviantart.net/3e0e/f/2015/1'
                               '37/8/5/the_witcher_3__wild_hunt___icon_by_'
                               'blagoicons-d8tt0rh.png'),
                 'payload': '{"attribute": "heavy_games", "value": 1}'},
                {'content_type': 'text',
                 'title': 'Só um Diablo II mesmo',
                 'image_url': ('http://2.bp.blogspot.com/_phtIMdxamd0/'
                               'TQtyT4p2VMI/AAAAAAAAAII/cYZHBMokYHc/s1600/'
                               'Diablo+II+new+1.png'),
                 'payload': '{"attribute": "light_games", "value": 1}'},
            ]

    def next(self, user_id):
        user_state = models.UserState.objects.get(user=user_id)
        user_state.state = self.next_state
        user_state.save()


class IsForWorkState(State):
    name = 'is_for_work'

    def __init__(self):
        self.user_response = None
        self.next_state = 'is_for_work'

    def handle_message(self, message):
        if 'message' in message:
            self.user_response = sentiment.classify(message['message']['text'])
            self.user_profile = models.UserProfile.objects.get_or_create(
                user=message['sender']['id'],
                defaults={
                    'is_student': 0,
                    'documents_sheets': 0,
                    'image_video': 0,
                    'performance': 0,
                    'heavy_games': 0,
                    'light_games': 0,
                    'cost_benefit': 0,
                }
            )[0]

    def text(self, user_infos):

        if self.user_response is None:
            return ('Desculpe, não consegui entender o que você disse. '
                    'Pode repetir?')
        elif self.user_response == 'pos':
            self.user_profile.is_student = 1
            self.user_profile.save()
            text = ('Legal! Podemos conversar sobre o que você estuda num '
                    'outro momento :) Mas vamos continuar com as nossas '
                    'perguntas! Você pretende usar o notebook para trabalhar?')
        else:
            text = ('Ok! Depois podemos conversar sobre o que você estudou, '
                    'o que acha? :) Mas, por enquanto, vamos continuar com as '
                    'nossas perguntas! Você pretende usar o notebook para '
                    'trabalhar?')
        self.next_state = 'which_works'
        return text

    def quick_replies(self, user_infos):
        if self.user_response:
            return [
                {'content_type': 'text',
                 'title': 'Para trabalho não',
                 'image_url': ('http://wfarm2.dataknet.com/static/'
                               'resources/icons/set21/3d6cfa22dd6.png'),
                 'payload': '{"stop": true}'},
                {'content_type': 'text',
                 'title': 'Edição de textos',
                 'image_url': ('https://icon-icons.com/icons2/908/PNG/512/'
                               'pencil-and-two-white-sheets-of-paper_icon-'
                               'icons.com_70650.png'),
                 'payload': '{"attribute": "documents_sheets", "value": 1}'},
                {'content_type': 'text',
                 'title': 'Edição de fotos/vídeos',
                 'image_url': ('https://d30y9cdsu7xlg0.cloudfront.net/'
                               'png/16203-200.png'),
                 'payload': '{"attribute": "image_video", "value": 1}'},
                {'content_type': 'text',
                 'title': 'Alta performance',
                 'image_url': ('https://d30y9cdsu7xlg0.cloudfront.net/'
                               'png/366778-200.png'),
                 'payload': '{"attribute": "performance", "value": 1}'},
            ]
        else:
            return None

    def next(self, user_id):
        user_state = models.UserState.objects.get(user=user_id)
        user_state.state = self.next_state
        user_state.save()


class IsStudentState(State):
    name = 'is_student'

    def __init__(self):
        self.user_response = None
        self.next_state = 'is_student'

    def handle_message(self, message):
        if 'message' in message:
            self.user_response = sentiment.classify(message['message']['text'])

    def text(self, user_infos):
        if self.user_response is None:
            return ('Desculpe, não consegui entender o que você disse. '
                    'Pode repetir?')
        elif self.user_response == 'pos':
            self.next_state = 'is_for_work'
            return ('Certo, entao vamos para primeira pergunta! '
                    'Você é estudante?')
        else:
            self.next_state = 'welcome'
            return ('Ah :( Tudo bem, fica pra proxima! Volte quando tiver '
                    'mais tempo :)')

    def next(self, user_id):
        user_state = models.UserState.objects.get(user=user_id)
        user_state.state = self.next_state
        user_state.save()


class WelcomeState(State):
    name = 'welcome'

    def text(self, user_infos):
        name = user_infos['first_name']
        return ("Olá, {}! Tudo bem com você? Eu posso te ajudar a escolher um"
                " notebook ideal pra você! Basta responder algumas perguntas "
                "que eu farei uma análise do seu perfil e direi o melhor "
                "notebook para você! Vamos começar?".format(name))

    def handle_message(self, message):
        pass

    def next(self, user_id):
        user_state = models.UserState.objects.get(user=user_id)
        user_state.state = 'is_student'
        user_state.save()


class Context:
    states = {
        'welcome': WelcomeState(),
        'is_student': IsStudentState(),
        'is_for_work': IsForWorkState(),
        'which_works': WhichWorksState(),
        'which_games': WhichGamesState(),
        'price': PriceState(),
    }

    def __init__(self, state):
        self._state = self.states[state]

    def process_message(self, message, user_id):
        user_infos = facebook.get_user_infos(user_id)
        self._state.handle_message(message)
        response = {
            'text': self._state.text(user_infos),
            'attachment': self._state.attachment(user_infos),
            'quick_replies': self._state.quick_replies(user_infos),
        }
        self._state.next(user_id)
        return response
