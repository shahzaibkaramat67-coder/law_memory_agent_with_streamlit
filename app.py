import streamlit as st

from agent import build_conversation
from mian import (
    SUPPORTED_PROVIDERS,
    get_configured_api_key,
    get_default_base_url,
    get_default_model,
    get_model,
)


SUGGESTIONS = {
    "Understand a lease clause": (
        "What should I look for in a residential lease before signing?"
    ),
    "Prepare for a legal meeting": (
        "How can I prepare for an initial meeting with a lawyer?"
    ),
    "Learn about small claims": (
        "What are the usual steps in a small-claims case?"
    ),
}

st.set_page_config(
    page_title="Legal Desk",
    page_icon=":material/account_balance:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_model(provider, model_name, api_key, base_url):
    return get_model(provider, model_name, api_key, base_url)


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at 50% 0%, rgba(225, 214, 191, 0.20), transparent 42%),
            #f8f7f4;
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    [data-testid="stSidebar"] {
        background: #f1efe9;
        border-right: 1px solid #e5e1d8;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }
    .block-container {
        max-width: 940px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }
    .brand {
        color: #263b37;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        margin: 0.1rem 0 0;
    }
    .brand-note {
        color: #77786f;
        font-size: 0.72rem;
        letter-spacing: 0.13em;
        margin: 0.1rem 0 1.5rem;
        text-transform: uppercase;
    }
    .eyebrow {
        align-items: center;
        color: #6e776e;
        display: flex;
        font-size: 0.76rem;
        font-weight: 600;
        gap: 0.5rem;
        letter-spacing: 0.1em;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
    }
    .eyebrow-mark {
        background: #bd9b64;
        border-radius: 50%;
        height: 7px;
        width: 7px;
    }
    .hero-title {
        color: #263b37;
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(2.1rem, 4.2vw, 3.35rem);
        font-weight: 500;
        letter-spacing: -0.045em;
        line-height: 1.1;
        margin: 0;
        max-width: 720px;
    }
    .hero-copy {
        color: #73766f;
        font-size: 1rem;
        line-height: 1.7;
        margin: 0.85rem 0 1.8rem;
        max-width: 640px;
    }
    .section-label {
        color: #626b64;
        font-size: 0.79rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin: 0.7rem 0 0.75rem;
    }
    .legal-note {
        border-top: 1px solid #e8e5de;
        color: #77786f;
        font-size: 0.77rem;
        line-height: 1.6;
        margin-top: 1.4rem;
        padding-top: 1rem;
    }
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid #ebe8e0;
        border-radius: 16px;
        margin-bottom: 0.8rem;
        padding: 1rem 1.15rem;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #f0eee8;
    }
    [data-testid="stChatInput"] {
        border-color: #dedbd2;
        border-radius: 16px;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #789188;
        box-shadow: 0 0 0 1px #789188;
    }
    [data-testid="stButton"] button {
        border-radius: 12px;
        min-height: 2.8rem;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        border-color: #e0ddd5;
        background: rgba(255, 255, 255, 0.55);
    }
    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1.4rem;
        }
        .hero-copy {
            font-size: 0.94rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.session_state.setdefault("messages", [])
st.session_state.setdefault("jurisdiction", "")

with st.sidebar:
    st.markdown('<p class="brand">Legal Desk</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="brand-note">A calmer place to start</p>',
        unsafe_allow_html=True,
    )

    if st.button(
        "New conversation",
        icon=":material/add_comment:",
        width="stretch",
    ):
        st.session_state["messages"] = []
        st.rerun()

    st.space("medium")
    st.markdown("**Conversation context**")
    jurisdiction = st.text_input(
        "Jurisdiction",
        key="jurisdiction",
        placeholder="e.g. California, United States",
        help=(
            "Legal rules vary by location. Add a country, state, or region "
            "to help frame your questions."
        ),
    )
    st.markdown("**API settings**")
    provider = st.selectbox(
        "Provider",
        SUPPORTED_PROVIDERS,
        key="api_provider",
        help="Choose the AI service and API endpoint for this session.",
    )
    model_name = st.text_input(
        "Model",
        value=get_default_model(provider),
        key=f"api_model_{provider}",
        help="Enter any model name supported by the selected provider.",
    )
    api_key = ""
    if provider != "Ollama":
        configured_api_key = get_configured_api_key(provider)
        api_key = st.text_input(
            "API key",
            type="password",
            key=f"api_key_{provider}",
            placeholder=(
                "Using environment key"
                if configured_api_key
                else "Enter your API key"
            ),
            help="Kept in this Streamlit session; it is not written to a file.",
        )
        api_key = api_key.strip() or configured_api_key

    base_url = ""
    if provider in ("OpenAI-compatible", "Ollama"):
        base_url = st.text_input(
            "API base URL",
            value=get_default_base_url(provider),
            key=f"api_base_url_{provider}",
            placeholder="https://your-provider.example/v1",
            help=(
                "For an OpenAI-compatible service, enter its API base URL. "
                "For Ollama, use the address of your local Ollama server."
            ),
        ).strip()

    api_key_configured = provider == "Ollama" or bool(api_key)
    if not api_key_configured:
        st.warning(
            f"{provider} API key not configured. Enter your key above or set "
            "the provider's API key environment variable.",
            icon=":material/key_off:",
        )
    st.caption(f"{provider} · {model_name}")

    st.space("large")
    st.markdown(
        """
        <div class="legal-note">
            <strong>Helpful, not a substitute for counsel.</strong><br>
            Answers are general information, not legal advice. For a decision
            that affects your rights, speak with a qualified lawyer.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="eyebrow"><span class="eyebrow-mark"></span> Legal information, made clearer</div>
    <h1 class="hero-title">A thoughtful first step<br>toward understanding the law.</h1>
    <p class="hero-copy">
        Ask a question in plain language. Get a clear starting point, useful
        context, and help understanding what to ask next.
    </p>
    """,
    unsafe_allow_html=True,
)

if not st.session_state["messages"]:
    st.markdown('<p class="section-label">A few places to begin</p>', unsafe_allow_html=True)
    suggestion_columns = st.columns(3)
    selected_prompt = None
    for column, (label, question) in zip(
        suggestion_columns, SUGGESTIONS.items()
    ):
        with column:
            if st.button(
                label,
                key=f"suggestion_{label}",
                icon=":material/arrow_outward:",
                width="stretch",
            ):
                selected_prompt = question
else:
    for message in st.session_state["messages"]:
        with st.chat_message(
            message["role"],
            avatar=(
                ":material/account_balance:"
                if message["role"] == "assistant"
                else ":material/person:"
            ),
        ):
            st.markdown(message["content"])
    selected_prompt = None

prompt = st.chat_input(
    "Ask a legal question...",
    max_chars=4000,
)
prompt = selected_prompt or prompt

if prompt:
    if not api_key_configured:
        st.error(
            f"I can’t answer yet because the {provider} API key is missing. "
            "Enter your key in the API settings in the sidebar."
        )
    elif provider == "OpenAI-compatible" and not base_url:
        st.error(
            "Enter an API base URL for the OpenAI-compatible provider in the sidebar."
        )
    else:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=":material/person:"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=":material/account_balance:"):
            with st.spinner("Putting together a clear answer..."):
                model = load_model(provider, model_name, api_key, base_url)
                response = model.invoke(
                    build_conversation(
                        st.session_state["messages"][:-1],
                        prompt,
                        jurisdiction,
                    )
                )
            content = response.content
            if isinstance(content, str):
                answer = content
            elif isinstance(content, list):
                answer = "\n".join(
                    block["text"]
                    for block in content
                    if isinstance(block, dict)
                    and isinstance(block.get("text"), str)
                )
            else:
                answer = str(content)
            st.markdown(answer)
        st.session_state["messages"].append(
            {"role": "assistant", "content": answer}
        )

st.caption(
    "Legal Desk can make mistakes. Please verify important information with a "
    "qualified legal professional."
)
