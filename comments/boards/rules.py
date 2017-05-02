

rules = {
    'google.com': {
        'regex': [

        ],
        'qs': {

        }
    },
    'youtube.com': {
        'regex': {
            '^/user/([^/]+).*$': '/user/$1',
            '^/channel/([^/]+).*$': '/channel/$1',
        },
        'qs': {
            '/watch': ['v'],
            '/playlist': ['list']
        }
    },
    'facebook': {

    },
    'wikipedia.org': {

    }
}
