# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormValidationAction


class ActionSayIdNumber(Action):

    def name(self) -> Text:
        return "action_say_id_number"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        id_number = tracker.get_slot("IDNUMBER")
        if not id_number or len(id_number) != 12:
            dispatcher.utter_message(text="Вы не указали ваш ИИН или он неверной длины.")
            return []

        first_half = id_number[:6]
        second_half = id_number[6:]

        
        return [SlotSet("FIRSTHALF", first_half), SlotSet("SECONDHALF", second_half)]
    
class ActionConfirmFirstHalf(Action):

    def name(self) -> Text:
        return "action_confirm_first_half"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        first_half = tracker.get_slot("FIRSTHALF")
        dispatcher.utter_message(text=f"Ваш первая половина ИИН такая: {first_half}. Она правильная?")

        attempts_firsthalf = tracker.get_slot("attempts_firsthalf") or 0

        if attempts_firsthalf >= 3:
            dispatcher.utter_message(text="Вы превысили количество попыток для подтверждения первых 6 цифр.")
            dispatcher.utter_message(template="utter_attempts_exceeded")
            return [SlotSet("attempts_firsthalf", 0)]

        if tracker.latest_message['intent'].get('name') == "confirm":
            dispatcher.utter_message(text="Теперь введите вторую половину ИИН.")
            return [SlotSet("attempts_firsthalf", 0), SlotSet("first_half_confirmed", True)] 
        else:
            dispatcher.utter_message(text=f"Пожалуйста, введите правильную первую половину ИИН. У вас осталось {3 - attempts_firsthalf} попытки.")
            return [SlotSet("attempts_firsthalf", attempts_firsthalf + 1)]
    
class ActionConfirmSecondHalf(Action):

    def name(self) -> Text:
        return "action_confirm_second_half"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        second_half = tracker.get_slot("SECONDHALF")
        attempts_secondhalf = tracker.get_slot("attempts_secondhalf") or 0
        dispatcher.utter_message(text=f"Ваш первая половина ИИН такая: {second_half}. Она правильная?")


        if attempts_secondhalf >= 3:
            dispatcher.utter_message(text="Вы превысили количество попыток для подтверждения вторых 6 цифр.")
            dispatcher.utter_message(template="utter_attempts_exceeded")
            return [SlotSet("attempts_secondhalf", 0)] 

        if tracker.latest_message['intent'].get('name') == "confirm":
            dispatcher.utter_message(text="Ваш ИИН подтвержден.")
            return [SlotSet("attempts_secondhalf", 0), SlotSet("second_half_confirmed", True)] 
        else:
            dispatcher.utter_message(text=f"Пожалуйста, введите правильную вторую половину ИИН. У вас осталось {3 - attempts_secondhalf} попытки.")
            return [SlotSet("attempts_secondhalf", attempts_secondhalf + 1)]
        
class ValidateConfirmHalfesForm(FormValidationAction):
    def name(self) -> str:
        return "validate_confirm_halfes_form"

    async def validate_first_half_confirmed(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> dict:
        if tracker.latest_message['intent'].get('name') == "confirm":
            dispatcher.utter_message(text="Первая половина ИИН подтверждена.")
            return {"first_half_confirmed": True, "FIRSTHALF": slot_value}
        else:
            dispatcher.utter_message(text="Первая половина ИИН не подтверждена. Пожалуйста, введите её снова.")
            return {"FIRSTHALF": None, "first_half_confirmed": False}

    async def validate_second_half_confirmed(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> dict:
        if tracker.latest_message['intent'].get('name') == "confirm":
            dispatcher.utter_message(text="Вторая половина ИИН подтверждена.")
            return {"second_half_confirmed": True, "SECONDVALUE": slot_value}
        else:
            dispatcher.utter_message(text="Вы не потвердили. Пожалуйста, введите её снова.")
            return {"SECONDHALF": None, "second_half_confirmed": False}