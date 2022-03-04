import interactions
from ..const import METADATA

cmd = dict(
    name="mod",
    description="Handles all moderation aspects.",
    scope=METADATA["guild"],
    options=[
        interactions.Option(
            type=interactions.OptionType.SUB_COMMAND_GROUP,
            name="member",
            description="Handles moderating a member.",
            options=[
                interactions.Option(
                    type=interactions.OptionType.SUB_COMMAND,
                    name="ban",
                    description="Bans a user.",
                    options=[
                        interactions.Option(
                            type=interactions.OptionType.USER,
                            name="user",
                            description="The user you wish to ban.",
                            required=True,
                        ),
                        interactions.Option(
                            type=interactions.OptionType.STRING,
                            name="reason",
                            description="The reason behind why you want to ban them.",
                            required=False,
                        ),
                    ],
                ),
                interactions.Option(
                    type=interactions.OptionType.SUB_COMMAND,
                    name="unban",
                    description="Unbans a user.",
                    options=[
                        interactions.Option(
                            type=interactions.OptionType.INTEGER,
                            name="id",
                            description="The ID of the user you wish to unban.",
                            required=True,
                        ),
                        interactions.Option(
                            type=interactions.OptionType.STRING,
                            name="reason",
                            description="The reason behind why you want to ban them.",
                            required=False,
                        ),
                    ],
                ),
                interactions.Option(
                    type=interactions.OptionType.SUB_COMMAND,
                    name="kick",
                    description="Kicks a user.",
                    options=[
                        interactions.Option(
                            type=interactions.OptionType.USER,
                            name="user",
                            description="The user you wish to kick.",
                            required=True,
                        ),
                        interactions.Option(
                            type=interactions.OptionType.STRING,
                            name="reason",
                            description="The reason behind why you want to ban them.",
                            required=False,
                        ),
                    ],
                ),
                interactions.Option(
                    type=interactions.OptionType.SUB_COMMAND,
                    name="warn",
                    description="Warns a user.",
                    options=[
                        interactions.Option(
                            type=interactions.OptionType.USER,
                            name="user",
                            description="The user you wish to warn.",
                            required=True,
                        ),
                        interactions.Option(
                            type=interactions.OptionType.STRING,
                            name="reason",
                            description="The reason behind why you want to ban them.",
                            required=False,
                        ),
                    ],
                ),
            ],
        ),
    ]
)