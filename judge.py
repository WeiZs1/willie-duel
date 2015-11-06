"""
judge.py - edited clone of a mIRC script to let users case each other adapted to let users sue each other instead
Copyright 2015 dgw
"""

from __future__ import division
from willie import module, tools
import random
import time


TIMEOUT = 600


STRINGS = {
	'NOJUDGE':			["You can't sue the judge! Try someone else.",
                                         "Thou shalt not sue the judge. Find another target for your bullying."],
	'WHO2SUE':			["Who did you want to sue?",
                                        "You forgot to name the target of your lawsuit!"],
	'NON_EXISTANT':			"You can't sue people who don't exist!",
	'CRIME':	    		["indecent exposure in the workplace",
	    				"raping a block of cheese",
                                        "slapping the President on national television",
		    			"parking in front of a fire hydrant",
				    	 "the theft of a celebrity's bath towel"],
}
@module.commands('sue')
@module.require_chanmsg
def case(bot, trigger):
    time_since = time_since_case(bot, trigger.nick)
    if time_since < TIMEOUT:
        bot.notice("You must wait %d seconds until your next case." % (TIMEOUT - time_since), trigger.nick)
        return module.NOLIMIT
    target = tools.Identifier(trigger.group(3) or None)
    if not target:
        bot.reply(random.choice(STRINGS['WHO2SUE']))
        return module.NOLIMIT
    if target == bot.nick:
        bot.say(random.choice(STRINGS['NOJUDGE']))
        return module.NOLIMIT
    if target.lower() not in bot.privileges[trigger.sender.lower()]:
        bot.say("You can't sue people who don't exist!")
        return module.NOLIMIT
    bot.say("%s takes %s to court." % (trigger.nick, target))
    participants = [trigger.nick, target]
    random.shuffle(participants)
    winner = participants.pop()
    loser = participants.pop()
    if loser == target:
        if bot.privileges[trigger.sender.lower()][bot.nick.lower()] >= module.OP:
          bot.write(['KICK', trigger.sender, loser], "You have been found guilty of " +random.choice(STRINGS['CRIME']) + "!")
        else:	
        	bot.say("%s is found guilty of " % target + random.choice(STRINGS['CRIME']) + "!" )
        	
    if winner == target:
        	bot.say("%s is found not guilty!" % target)
    bot.db.set_nick_value(trigger.nick, 'case_last', time.time())
    case_finished(bot, winner, loser)


@module.commands('cases')
def cases(bot, trigger):
    target = trigger.group(3) or trigger.nick
    wins, losses = get_cases(bot, target)
    total = wins + losses
    win_rate = wins / total * 100
    bot.say("%s has won %d out of %d cases (%.2f%%)." % (target, wins, total, win_rate))


def get_cases(bot, nick):
    wins = bot.db.get_nick_value(nick, 'case_wins') or 0
    losses = bot.db.get_nick_value(nick, 'case_losses') or 0
    return wins, losses


def time_since_case(bot, nick):
    now = time.time()
    last = bot.db.get_nick_value(nick, 'case_last') or 0
    return abs(now - last)


def update_cases(bot, nick, won=False):
    wins, losses = get_cases(bot, nick)
    if won:
        bot.db.set_nick_value(nick, 'case_wins', wins + 1)
    else:
        bot.db.set_nick_value(nick, 'case_losses', losses + 1)


def case_finished(bot, winner, loser):
    update_cases(bot, winner, True)
    update_cases(bot, loser, False)
