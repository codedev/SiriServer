#!/usr/bin/python
# -*- coding: utf-8 -*-

#author: AlphaBetaPhi <beta@alphabeta.ca>
#todo: check for existing alarms, delete alarms, update alarms, add original commands aka wake me up/tomorrow morning/midnight/etc.
#project: SiriServer
#commands: set an alarm for HH:MM AM/PM
#          set an alarm for HH AM/PM
#          set an alarm for HH AM/PM <called/labeled/named> <[word 1] [word 2] [word 3]>
#comments: feel free to email any comments/bug/updates

import re
from fractions import Fraction
from plugin import *
from siriObjects.baseObjects import AceObject, ClientBoundCommand
from siriObjects.uiObjects import AddViews, AssistantUtteranceView
from siriObjects.systemObjects import DomainObject
from siriObjects.alarmObjects import *

class alarmPlugin(Plugin):
    localizations = {
        'Alarm': {
            "settingAlarm": {
                "en-US": u"Setting the Alarm\u2026",
                "fr-FR": u"Réglage de l'alarme\u2026"
            }, "alarmWasSet": {
                "en-US": "Your alarm is set for {0}:{1} {2}.",
                "fr-FR": u"Votre alarme est programmée pour {0}:{1} {2}"
            }, "alarmSetWithLabel": {
                "en-US": "Your alarm {0} {1} is set for {2}:{3} {4}.",
                "fr-FR": u"Votre alarme {0} {1} est programmée pour {2}:{3} {4}"
            }
        }
    }

    res = {
        'setAlarm': {
            'en-US': '.*set.* alarm for.* (0?[1-9]|1[012])([0-5]\d)?\s?([APap][mM])\s?(\bcalled|named|labeled\b)?\s?(([a-z0-9]{1,7}\s)?([a-z0-9]{1,7})\s?([a-z0-9]{1,7}))?',
            'fr-FR': u'.*(programme|regle|règle|met|mai).*(alarme|reveil|réveil)([^0-9]+)([0-2]?[0-9])([^0-9]+)?([0-5]?[0-9])?\s?(\appelée|appel|nommée|nommee|labellé|labelle\b)?\s?(([a-z0-9]{1,7}\s)?([a-z0-9]{1,7})\s?([a-z0-9]{1,7}))?'
        }
    }

    @register("en-US", res['setAlarm']['en-US'])
    @register("fr-FR", res['setAlarm']['fr-FR'])
    def setAlarm(self, speech, language):
        alarmString = re.match(alarmPlugin.res['setAlarm'][language], speech, re.IGNORECASE)

        if language == 'fr-FR':
            labelGroupId = 8
            alarmHour = int(alarmString.group(4))
            alarm24Hour = alarmHour
            alarmMinutes = alarmString.group(6)
            alarmAMPM = ""
            alarmLabelExists = alarmString.group(labelGroupId)
        else:
            labelGroupId = 4
            alarmHour = int(alarmString.group(1))
            alarm24Hour = alarmHour
            alarmMinutes = alarmString.group(2)
            alarmAMPM = alarmString.group(3)
            alarmLabelExists = alarmString.group(labelGroupId)

        #check if we are naming the alarm
        if alarmLabelExists == None:
            alarmLabel = None
        else:
            alarmLabel = alarmString.group(labelGroupId)

        #the siri alarm object requires 24 hour clock
        if (alarmAMPM == "pm" and alarmHour != 12):
            alarm24Hour += 12
        if alarmMinutes == None:
            alarmMinutes = "00"
        else:
            alarmMinutes = int(alarmMinutes.strip())
        view = AddViews(self.refId, dialogPhase="Reflection")
        view.views = [
            AssistantUtteranceView(
                speakableText=alarmPlugin.localizations['Alarm']['settingAlarm'][language],
                dialogIdentifier="Alarm#settingAlarm")]
        self.sendRequestWithoutAnswer(view)

        #create the alarm
        alarm = AlarmObject(alarmLabel, int(alarmMinutes), alarm24Hour, None, 1)
        response = self.getResponseForRequest(AlarmCreate(self.refId, alarm))
        #print(alarmPlugin.localizations['Alarm']['alarmWasSet'][language].format(alarmHour, alarmMinutes, alarmAMPM))
        view = AddViews(self.refId, dialogPhase="Completion")
        if alarmLabel == None:
            view1 = AssistantUtteranceView(speakableText=alarmPlugin.localizations['Alarm']['alarmWasSet'][language].format(alarmHour, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmWasSet")
        else:
            view1 = AssistantUtteranceView(speakableText=alarmPlugin.localizations['Alarm']['alarmSetWithLabel'][language].format(alarmLabelExists, alarmLabel, alarmHour, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmSetWithLabel")
        view2 = AlarmSnippet(alarms=[alarm])
        view.views = [view1, view2]
        self.sendRequestWithoutAnswer(view)
        self.complete_request()
        
        
    wake = {
        'wakeup': {
            'en-US': '.*wake.* up at.* (0?[1-9]|1[012])([0-5]\d)?\s?([APap][mM])\s?(\bcalled|named|labeled\b)?\s?(([a-z0-9]{1,7}\s)?([a-z0-9]{1,7})\s?([a-z0-9]{1,7}))?',
            
        }
    }

    @register("en-US", wake['wakeup']['en-US'])    
    def wakeup(self, speech, language):
        alarmString = re.match(alarmPlugin.wake['wakeup'][language], speech, re.IGNORECASE)

        if language == 'fr-FR':
            labelGroupId = 8
            alarmHour = int(alarmString.group(4))
            alarm24Hour = alarmHour
            alarmMinutes = alarmString.group(6)
            alarmAMPM = ""
            alarmLabelExists = alarmString.group(labelGroupId)
        else:
            labelGroupId = 4
            alarmHour = int(alarmString.group(1))
            alarm24Hour = alarmHour
            alarmMinutes = alarmString.group(2)
            alarmAMPM = alarmString.group(3)
            alarmLabelExists = alarmString.group(labelGroupId)

        #check if we are naming the alarm
        if alarmLabelExists == None:
            alarmLabel = None
        else:
            alarmLabel = alarmString.group(labelGroupId)

        #the siri alarm object requires 24 hour clock
        if (alarmAMPM == "pm" and alarmHour != 12):
            alarm24Hour += 12
        if alarmMinutes == None:
            alarmMinutes = "00"
        else:
            alarmMinutes = int(alarmMinutes.strip())
        view = AddViews(self.refId, dialogPhase="Reflection")
        view.views = [
            AssistantUtteranceView(
                speakableText=alarmPlugin.localizations['Alarm']['settingAlarm'][language],
                dialogIdentifier="Alarm#settingAlarm")]
        self.sendRequestWithoutAnswer(view)

        #create the alarm
        alarm = AlarmObject(alarmLabel, int(alarmMinutes), alarm24Hour, None, 1)
        response = self.getResponseForRequest(AlarmCreate(self.refId, alarm))
        #print(alarmPlugin.localizations['Alarm']['alarmWasSet'][language].format(alarmHour, alarmMinutes, alarmAMPM))
        view = AddViews(self.refId, dialogPhase="Completion")
        if alarmLabel == None:
            view1 = AssistantUtteranceView(speakableText=alarmPlugin.localizations['Alarm']['alarmWasSet'][language].format(alarmHour, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmWasSet")
        else:
            view1 = AssistantUtteranceView(speakableText=alarmPlugin.localizations['Alarm']['alarmSetWithLabel'][language].format(alarmLabelExists, alarmLabel, alarmHour, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmSetWithLabel")
        view2 = AlarmSnippet(alarms=[alarm])
        view.views = [view1, view2]
        self.sendRequestWithoutAnswer(view)
        self.complete_request()