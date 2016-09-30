from modeltranslation.translator import translator, TranslationOptions
from molo.profiles.models import SecurityQuestion


class SecurityQuestionTranslationOptions(TranslationOptions):
    fields = ("question", )

translator.register(SecurityQuestion, SecurityQuestionTranslationOptions)
