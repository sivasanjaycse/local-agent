try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from google import genai
import config

api_key = config.GEMINI_API_KEY

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model=config.GEMINI_MODEL,
    contents="Say hello in one short sentence."
)

print(response.text)
