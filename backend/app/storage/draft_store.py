from copy import deepcopy

from app.models.listing import ListingDraft

_drafts: dict[str, ListingDraft] = {}


def save_draft(draft: ListingDraft) -> ListingDraft:
    _drafts[draft.draftId] = draft
    return deepcopy(draft)


def get_draft(draft_id: str) -> ListingDraft | None:
    draft = _drafts.get(draft_id)
    return deepcopy(draft) if draft else None
