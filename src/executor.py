#!/usr/bin/env python2
# -*- coding: utf-8 -*

import sys
import argparse
import select
import qi

class Authenticator:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # This method is expected by libqi and must return a dictionary containing
    # login information with the keys 'user' and 'token'.
    def initialAuthData(self):
        return {'user': self.username, 'token': self.password}


class AuthenticatorFactory:
    def __init__(self, username = "nao", password = "nao"):
        self.username = username
        self.password = password

    # This method is expected by libqi and must return an object with at least
    # the `initialAuthData` method.
    def newAuthenticator(self):
        return Authenticator(self.username, self.password)

def make_application():
    app = qi.Application(sys.argv)
    factory = AuthenticatorFactory()
    app.session.setClientAuthenticatorFactory(factory)
    return app


class SpeechHelper:
    def __init__(self, session):
        session.waitForService("ActuationPrivate")
        self.actuationPriv = session.service("ActuationPrivate")
        session.waitForService("Actuation")
        self.actuation = session.service("Actuation")
        session.waitForService("ALAutonomousLife")
        life = session.service("ALAutonomousLife")
        session.waitForService("ContextFactory")
        contextFact = session.service("ContextFactory")
        focus = life._preemptFocusForRemote()

        session.waitForService("ALTextToSpeech")
        self.tts = session.service("ALTextToSpeech")

        self.context = contextFact.makeContext()
        self.context.focus.setValue(focus)



    def talk(self, text):
        try:
            self.tts.say(text)
        except RuntimeError as e:
            raise RuntimeError("Problem when calling say : " + e.message)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()

    app = make_application()
    app.start()

    helper = SpeechHelper(app.session)
    helper.talk('Hi Sera')
