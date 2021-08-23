from beymax.bots.core import CoreBot
from beymax.bots import utils
from beymax.bots.args import Arg
import os

def init():
    bot = CoreBot()

    # Bot commands


    @bot.add_command('room', Arg('name', help="Name for the room"))
    async def cmd_room(self, message, name):
        """
        `$!room (name)` : Adds a new room reservation
        """
        async with utils.DBView('rooms') as db:
            if name in db['rooms']:
                return await self.send_message(
                    message.channel,
                    "This room is already taken"
                )
            else:
                shorthands = {val for key, val in db['rooms'].items()}
                for letter in name.lower():
                    if letter != 'x' and letter not in shorthands:
                        db['rooms'][name] = letter
                        return await self.send_message(
                            message.channel,
                            "New room created: {} ({})".format(name, letter)
                        )

                if len(name) <= 4 and not name.lower().startswith('x'):
                    db['rooms'][name] = name
                    return await self.send_message(
                        message.channel,
                        "New room created: {} ({})".format(name, name)
                    )
                shorthand = 'x{}{}'.format(name[0], os.urandom(1).hex()).lower()
                while shorthand in shorthands:
                    shorthand = 'x{}{}'.format(name[0], os.urandom(1).hex()).lower()
                db['rooms'][name] = shorthand
                return await self.send_message(
                    message.channel,
                    "New room created: {} ({})".format(name, shorthand)
                )

    @bot.add_command('rooms')
    async def cmd_rooms(self, message):
        """
        `$!rooms` : Lists available rooms
        """
        async with utils.DBView(rooms={}) as db:
            await self.send_message(
                message.channel,
                "Here are the defined rooms: {}".format(
                    ', '.join(db['rooms'])
                )
            )


    # !new (size) (room) : Adds a new box, outputs box designation
    @bot.add_command('new', Arg('size', help="Box size"), Arg('room', help="Room name"))
    async def cmd_new(self, message, size, room):
        async with utils.DBView('boxes', 'rooms') as db:
            if room not in db['rooms']:
                return await self.send_message(
                    message.channel,
                    "No such room `{}`".format(room)
                )
            designation = '{}{}{}'.format(
                db['rooms'][room],
                size[0],
                os.urandom(1).hex()
            ).lower()
            while designation in db['boxes']:
                designation = '{}{}{}'.format(
                    db['rooms'][room],
                    size[0],
                    os.urandom(1).hex()
                ).lower()
            db['boxes'][designation] = {
                'size': size,
                'room': room,
                'manifest': 'Not Specified',
                'status': 'Not Specified (Packing)'
            }
            return await self.send_message(
                message.channel,
                "New box created: `{}`".format(designation)
            )

    # !manifest (designation) [text] : Gets or sets box manifest
    @bot.add_command('manifest', Arg('designation', help="Box designation"), Arg('manifest', help="Optional: Set box contents", remainder=True))
    async def cmd_manifest(self, message, designation, manifest):
        async with utils.DBView('boxes') as db:
            if designation not in db['boxes']:
                return await self.send_message(
                    message.channel,
                    "No such box `{}`".format(designation)
                )
            if manifest is None or len(manifest) == 0:
                return await self.send_message(
                    message.channel,
                    'Box contents: {}'.format(db['boxes'][designation]['manifest'])
                )
            db['boxes'][designation]['manifest'] = manifest
            return await self.send_message(
                message.channel,
                "Manifest updated"
            )

    # !move (designation) (status) : Updates box status
    @bot.add_command('move', Arg('designation', help='Box designation'), Arg('status', help="New location"))
    async def cmd_move(self, message, designation, status):
        async with utils.DBView('boxes') as db:
            if designation not in db['boxes']:
                return await self.send_message(
                    message.channel,
                    "No such box `{}`".format(designation)
                )
            db['boxes'][designation]['status'] = status
            return await self.send_message(
                message.channel,
                "Status updated"
            )

    # !where (desgination) : Gets box status
    @bot.add_command('where', Arg('designation', help='Box designation'))
    async def cmd_where(self, message, designation):
        async with utils.DBView(boxes={}) as db:
            if designation not in db['boxes']:
                return await self.send_message(
                    message.channel,
                    "No such box `{}`".format(designation)
                )
            return await self.send_message(
                message.channel,
                "Box `{}`: {}".format(
                    designation,
                    db['boxes'][designation]['status']
                )
            )

    # !list [room] : Lists all boxes or boxes for a specific room

    return bot

if __name__ == '__main__':
    init().run('***REMOVED***')
