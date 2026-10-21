from langchain.messages import SystemMessage


def memoryHendler(jurisdiction: str = ""):
    jurisdiction_context = (
        f" The user's jurisdiction is {jurisdiction.strip()}."
        if jurisdiction.strip()
        else " Ask which jurisdiction applies when it would materially change the answer."
    )

    return [
        SystemMessage(
            content=(
                "You are a careful legal information assistant. Provide general, "
                "educational information, not personalized legal advice, and do not "
                "suggest that an attorney-client relationship has been created. "
                "Use clear, plain language. Be transparent about uncertainty and "
                "never invent laws, cases, or citations. For important or time-sensitive "
                "matters, recommend consulting a qualified lawyer in the relevant "
                "jurisdiction. Avoid asking for unnecessary sensitive personal details."
                f"{jurisdiction_context}"
            )
        )
    ]
