from aiogram import Router, types

router = Router()

@router.message
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender
    By default, message handler will handle all message types
    (photos, stickers ect.)
    """
    try:
        await message.send_copy(message.chat.id)
    except TypeError:
        await message.answer("Nice try!")
