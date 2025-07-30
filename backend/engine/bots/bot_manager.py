import asyncio

from engine.bots.base_bot import BaseBot


class BotManager:
    """Manages lifecycle of market bots."""

    def __init__(self) -> None:
        """Instantiate new `BotManager`."""
        self._bots: dict[str, BaseBot] = {}
        self._tasks: dict[str, asyncio.Task] = {}

    def register_bot(self, bot: BaseBot) -> None:
        """Add a new bot to `BotManager` registry.
            
        Args:
            bot (BaseBot): Bot to register.

        """
        mpid = bot.mpid
        
        if mpid in self._bots:
            msg = f"Bot with id of {mpid} is already registered"
            raise KeyError(msg)

        self._bots[mpid] = bot

    def start_all(self) -> None:
        """Start all bots currently registered in `BotManager`."""
        bots: list[BaseBot] = list(self._bots.values())

        for bot in bots:
            mpid = bot.mpid

            if mpid in self._tasks:
                msg = f"Couldn't start bot with id {mpid}. (already running)"
                raise KeyError(msg)

            task = asyncio.create_task(bot.run())
            self._tasks[mpid] = task

    async def stop_all(self) -> None:
        """Stop all bots currently running."""
        tasks: list[asyncio.Task] = list(self._tasks.values())

        for t in tasks:
            t.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()

    def get_bot(self, mpid: str)-> BaseBot | None:
        """Get bot with market participant id as `mpid`.

        Args:
            mpid (str): Mpid of the bot you want to get.

        Returns:
            (BaseBot or None): Returns bot if exists, None otherwise.

        """
        return self._bots.get(mpid, None)

    def get_task(self, mpid: str) -> asyncio.Task | None:
        """Get `asyncio` Task associated with bot with `mpid`.

        Args:
            mpid (str): Mpid of the bot who owns the task.

        Returns:
            (asyncio.Task or None): Returns task if exists, None otherwise.

        """
        return self._tasks.get(mpid, None)




         
