import json
import logging
from copy import deepcopy

from openai import OpenAI
from pydantic import ValidationError

from app.config import get_settings
from app.models.ai_listing import AIListingDraft


class ListingGenerationError(Exception):
    pass


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You generate conservative eBay listing drafts from product photos and seller notes.

Rules:
- Follow the provided JSON schema exactly.
- Keep titles concise and factual.
- Keep subtitles short.
- Keep descriptions concise, concrete, and non-hypey.
- Treat seller notes as higher priority than uncertain visual inference.
- If brand, model, or specifics are uncertain, say so in missingInfoWarnings or itemSpecifics.
- Do not invent defects, accessories, or specifications with high confidence.
- Keep searchKeywords short and useful.
- Keep buyerQuestions practical and concise.
- Output only content that fits the schema.
"""


def _build_user_text(
    condition: str | None,
    known_issues: str | None,
    included_accessories: str | None,
    desired_price: str | None,
    seller_notes: str | None,
) -> str:
    sections = [
        "Generate an eBay listing draft from these product photos.",
        "Seller-provided context:",
        f"- condition: {condition or 'not provided'}",
        f"- known issues: {known_issues or 'not provided'}",
        f"- included accessories: {included_accessories or 'not provided'}",
        f"- desired price: {desired_price or 'not provided'}",
        f"- seller notes: {seller_notes or 'not provided'}",
        "",
        "Priorities:",
        "- Be conservative.",
        "- Prefer explicit seller notes over uncertain image inference.",
        "- Keep all text concise.",
        "- Include missing information as warnings instead of guessing.",
    ]
    return "\n".join(sections)


def _schema() -> dict:
    schema = deepcopy(AIListingDraft.model_json_schema())
    _enforce_closed_objects(schema)
    return schema


def _enforce_closed_objects(node: object) -> None:
    if isinstance(node, dict):
        if node.get("type") == "object":
            node["additionalProperties"] = False

        for value in node.values():
            _enforce_closed_objects(value)
    elif isinstance(node, list):
        for item in node:
            _enforce_closed_objects(item)


def _request_payload(image_data_urls: list[str], user_text: str) -> list[dict]:
    content: list[dict] = [{"type": "input_text", "text": user_text}]
    for image_data_url in image_data_urls:
        content.append(
            {
                "type": "input_image",
                "image_url": image_data_url,
                "detail": "low",
            }
        )

    return [{"role": "user", "content": content}]


def generate_listing_with_openai(
    image_data_urls: list[str],
    condition: str | None,
    known_issues: str | None,
    included_accessories: str | None,
    desired_price: str | None,
    seller_notes: str | None,
) -> AIListingDraft:
    settings = get_settings()

    if not settings.openai_api_key:
        raise ListingGenerationError("OpenAI API key is not configured on the backend.")

    client = OpenAI(api_key=settings.openai_api_key)
    user_text = _build_user_text(
        condition=condition,
        known_issues=known_issues,
        included_accessories=included_accessories,
        desired_price=desired_price,
        seller_notes=seller_notes,
    )
    last_error: Exception | None = None

    for _ in range(2):
        try:
            response = client.responses.create(
                model=settings.openai_model,
                input=_request_payload(image_data_urls=image_data_urls, user_text=user_text),
                instructions=SYSTEM_PROMPT,
                max_output_tokens=1400,
                reasoning={"effort": "low"},
                text={
                    "format": {
                        "type": "json_schema",
                        "strict": True,
                        "name": "listing_draft",
                        "schema": _schema(),
                    }
                },
            )
            payload = json.loads(response.output_text)
            return AIListingDraft.model_validate(payload)
        except (ValidationError, json.JSONDecodeError) as exc:
            last_error = exc
            continue
        except Exception as exc:
            logger.exception("OpenAI listing generation request failed")
            raise ListingGenerationError(
                f"OpenAI listing generation failed: {exc}"
            ) from exc

    raise ListingGenerationError(
        "The AI response could not be validated against the required listing format."
    ) from last_error
