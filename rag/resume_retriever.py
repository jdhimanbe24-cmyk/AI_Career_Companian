from rag.retriever import retrieve_context


def retrieve_resume_writing_context(role, section, user_input):

    query = f"""
    Resume writing guidelines for:
    Role: {role}
    Section: {section}

    User input:
    {user_input}

    Provide relevant professional resume writing guidelines,
    examples, formatting principles, and recommendations.
    """

    context = retrieve_context(
        query=query,
        role=role
    )

    return context