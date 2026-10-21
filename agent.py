from collections.abc import Mapping, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from memorySystem import memoryHendler


def build_conversation(
    history: Sequence[Mapping[str, str]],
    question: str,
    jurisdiction: str = "",
) -> list[BaseMessage]:
    messages = memoryHendler(jurisdiction)

    for turn in history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn["role"] == "assistant":
            messages.append(AIMessage(content=turn["content"]))

    messages.append(HumanMessage(content=question))
    return messages
