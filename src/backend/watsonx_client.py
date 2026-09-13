import os

_FALLBACK = "Situation summary unavailable - watsonx.ai not configured."


def generate_summary(prompt: str) -> str:
    """Call IBM watsonx.ai (granite-3-8b-instruct) with the given prompt and
    return the model's plain-text response.

    Returns the fallback message if credentials are absent or if the SDK call
    fails for any reason, so callers never need to handle exceptions.
    """
    api_key = os.getenv("WATSONX_API_KEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    # Guard: do not touch the SDK at all when credentials are missing
    if not api_key or not project_id:
        return _FALLBACK

    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

        credentials = Credentials(api_key=api_key, url=url)

        model = ModelInference(
            model_id="ibm/granite-3-8b-instruct",
            credentials=credentials,
            project_id=project_id,
            validate=False,
        )

        params = {GenTextParamsMetaNames.MAX_NEW_TOKENS: 200}

        result = model.generate_text(prompt=prompt, params=params)

        return result.strip() if result else _FALLBACK

    except Exception:
        return _FALLBACK
