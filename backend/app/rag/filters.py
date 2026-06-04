
def match_document_filter(meta: dict, document_id: str | None):
    if document_id is None:
        return True

    return str(meta.get("document_id")) == str(document_id)


def match_user_filter(meta: dict, user_id: str | None):
    if user_id is None:
        return True

    return str(meta.get("user_id")) == str(user_id)


def match_project_filter(meta: dict, project_id: str | None):
    if project_id is None:
        return True

    return str(meta.get("project_id")) == str(project_id)