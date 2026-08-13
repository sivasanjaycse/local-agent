try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from llm.gemini_client import GeminiIntentClassifier

classifier = GeminiIntentClassifier()

text = "Open Google Chrome"

result = classifier.classify(text)

print(result)
