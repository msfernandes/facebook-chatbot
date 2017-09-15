from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from recommendation import facebook, models
from recommendation.bot import states
import json


class WebhookView(View):
    http_method_names = [u'get', u'post']

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(WebhookView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        verify_token = request.GET.get('hub.verify_token')
        if verify_token == settings.FACEBOOK_VERIFY_TOKEN:
            return HttpResponse(request.GET.get('hub.challenge'))
        else:
            return HttpResponse('Invalid Token')

    def post(self, request):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    user_id = message['sender']['id']
                    facebook.send_message(
                        user_id,
                        'sender_action',
                        'typing_on'
                    )
                    user_state, _ = models.UserState.objects.get_or_create(
                        pk=user_id
                    )

                    state_handler = states.StateHandler(
                        user_state.state,
                        user_id
                    )
                    response = state_handler.process_message(message)
                    facebook.send_message(user_id, 'message', response)
                    if user_state.state == 'suggest':
                        facebook.send_message(
                            user_id, 'message',
                            {'text': ('Esses foram os resultados que se '
                                      'encaixaram no seu perfil :)\r\n\r\n'
                                      'Espero que eu tenha ajudado! Se '
                                      'você quiser repetir é só falar '
                                      'comigo.\r\n\r\nAté a próxima!')})
        return HttpResponse()
