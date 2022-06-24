import interactions
from ..const import METADATA

cmd = dict(
    name="tag",
    description="Handles \"tags\" aka. pre-written feeds for help.",
    scope=METADATA["guild"],
    options=[
        interactions.Option(
            type=interactions.OptionType.SUB_COMMAND,
            name="view",
            description="Views an existing tag.",
            options=[
                interactions.Option(
                    type=interactions.OptionType.STRING,
                    name="name",
                    description="The name of the tag you wish to view.",
                    required=True,
                    autocomplete=True,
                ),
            ],
        ),
        interactions.Option(
            type=interactions.OptionType.SUB_COMMAND,
            name="info",
            description="Gathers information about a tag.",
            options=[
                interactions.Option(
                    type=interactions.OptionType.STRING,
                    name="name",
                    description="The name of the tag you wish to gather information on.",
                    required=True,
                    autocomplete=True,
                )
            ]
        ),
        interactions.Option(
            type=interactions.OptionType.SUB_COMMAND,
            name="list",
            description="Lists all existing tags.",
            options=[],
        ),
        interactions.Option(
            type=interactions.OptionType.SUB_COMMAND,
            name="create",
            description="Creates a new tag.",
            options=[],
        ),
        interactions.Option(
            type=interactions.OptionType.SUB_COMMAND,
            name="edit",
            description="Edits an existing tag.",
            options=[
                interactions.Option(
                    type=interactions.OptionType.STRING,
                    name="name",
                    description="The name of the tag you wish to edit.",
                    required=True,
                    autocomplete=True,
                ),
            ],
        ),
        interactions.Option(
            type=interactions.OptionType.SUB_COMMAND,
            name="delete",
            description="Deletes an existing tag.",
            options=[
                interactions.Option(
                    type=interactions.OptionType.STRING,
                    name="name",
                    description="The name of the tag you wish to delete.",
                    required=True,
                    autocomplete=True,
                ),
            ],
        ),
    ],
)
