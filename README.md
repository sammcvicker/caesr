**srs** is a conceptual spaced repetition CLI built using LangChain and Click!

Unlike with normal flash cards, **srs** only requires you to name or describe what you'd like to remember.

## Coming Soon:

- **Varried Questions:** questions will be asked differently each time, sometimes requiring recall the other way around.
- **A Better Name:** **srs** is a bad name.
- **Sliding Scale Response Evaluation:** **srs** will soon use **supermemo2** and use an LLM-evaluated sliding scale for scoring.
- **Better Lists and Deck Management:** who needs all those words when you could auto-generate verbatim responses and use those when listing cards?!

## Installation

**pipx** makes for the easiest installation:

1. Download the [v0.1.1 wheel](./dist/srs-0.1.1-py3-none-any.whl)
2. Run `pipx install srs-0.1.1-py3-none-any.whl`
3. Simply configure **srs** and find a list of subcommands by running `srs`