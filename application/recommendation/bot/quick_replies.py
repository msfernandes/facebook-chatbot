work_replies = {
    'documents_sheets': {
        'content_type': 'text',
        'title': 'Edição de textos',
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


game_replies = {
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


cost_replies = {
    'expensive': {
        'content_type': 'text',
        'title': 'O melhor possível',
        'image_url': ('https://maxcdn.icons8.com/Share/icon/Finance/'
                      'money_bag_filled1600.png'),
        'payload': '{"attribute": "cost_benefit", "value": 0}'
    },
    'cheap': {
        'content_type': 'text',
        'title': 'O suficiente',
        'image_url': ('https://d30y9cdsu7xlg0.cloudfront.net/png/'
                      '48167-200.png'),
        'payload': '{"attribute": "cost_benefit", "value": 1}'
    }
}


def stop(text):
    return {
        'content_type': 'text',
        'title': text,
        'image_url': ('http://wfarm2.dataknet.com/static/'
                      'resources/icons/set21/3d6cfa22dd6.png'),
        'payload': '{"stop": true}'
    }
