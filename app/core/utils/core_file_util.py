import httpx
import base64


def wdg_image_as_base64(
    url: str, mime_type: str = "image/png", data_uri: bool = True
) -> str:
    """
    Fetch an image from a URL and return it as a base64-encoded string.
    - If `data_uri` is True (default), returns "data:{mime_type};base64,{encoded}"
    - If False, returns only the base64-encoded string.
    Returns empty string if URL is empty.
    """
    if not url:
        return None

    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError:
        return None

    encoded = base64.b64encode(response.content).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}" if data_uri else encoded
