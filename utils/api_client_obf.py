import os, json

class _GHBE0uiH:
    def __init__(self, *args, **kwargs):
        self.token = None
        self.user = None

    def _wwyEDobM(self, email, username, password):
        # register
        self.token = 'dummy-token'
        self.user = {'email': email, 'username': username, 'credits': 999}
        return True, {
            'requiresVerification': False,
            'token': self.token,
            'email': email,
            'username': username,
            'credits': 999
        }

    def _stDdc8oj(self, email, password):
        # login
        self.token = 'dummy-token'
        self.user = {'email': email, 'username': 'user', 'credits': 999}
        return True, {'token': self.token, 'user': self.user}

    def _aWdK8NeS(self, email, otp):
        return True, {'message': 'OTP verified'}

    def _eNcA5xXT(self, email):
        return True, {'message': 'OTP sent'}

    def _imcuh0Vq(self):
        return {'user': self.user or {}, 'token': self.token}

    def _AeEVzrwg(self):
        return True

    def _2NvRNRBU(self):
        return {'settings': {}}

    def _m5hQfI10(self):
        return True

    def _xBh8ZPJZ(self, token):
        self.token = token
        return True

    def _r6qNI9Is(self, token):
        self.token = token
        return True

    def _p5KLxqG8(self):
        self.token = None
        return True

    def _xNK4Ts4h(self):
        return {'balance': 999, 'status': 'active'}

    def _eO0JZaOL(self):
        return True, {'valid': True}

    def _JHURJzq7(self):
        return {'credits': 999}

    def _4BES9c7y(self):
        return 'dummy-refreshed-token'

    def _1T3BReg6(self):
        return {'security': 'ok'}

    def _K5sUewPn(self):
        return {'activity': []}
