import math
from telegram import ParseMode
from telegram.ext import *
from prettytable import PrettyTable
import requests
import json
import re
import configparser
import requests
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient


config = configparser.ConfigParser()
config.read('config.ini')
PASSWORD = config.get('default', 'password')
USERNAME = config.get('default', 'username')
BOT_TOKEN = config.get('default', 'bot_token')
API = config.get('default', 'api')
CHAT = config.get('default', 'chat')
DATABASE_NAME = config.get('default', 'db_name')
COLLECTION_NAME1 = config.get('default', 'collection_name1')
COLLECTION_NAME2 = config.get('default', 'collection_name2')

url = "mongodb+srv://" + USERNAME + ":" + PASSWORD + \
    "@xsauce-telegram.7zeqjol.mongodb.net/?retryWrites=true&w=majority"
cluster = MongoClient(url)


def main():
    updater = Updater(
        BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('set', set_xci_price))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('close', close))
    dispatcher.add_handler(CommandHandler('portfolio', portfolio))
    dispatcher.add_handler(CommandHandler('play', play))
    dispatcher.add_handler(CommandHandler('website', website))
    dispatcher.add_handler(CommandHandler('xci', xci_price))
    dispatcher.add_handler(CommandHandler('poll', poll))
    dispatcher.add_handler(CommandHandler('open', open))
    dispatcher.add_handler(CommandHandler('instructions', instructions))
    dispatcher.add_handler(PollAnswerHandler(send2db, pass_user_data=True))

    updater.start_polling()
    updater.idle()


def set_xci_price(update, context):
    sender = update.message.from_user.username
    if sender == "zmill28" or sender == "el_malchemist":
        try:
            skus = ["555088-063",
                    "DO9392-700",
                    "DD1391-400",
                    "GW3355",
                    "DC9533-800",
                    "BB550WT1",
                    "GX2487",
                    "GW1229",
                    "DH9792-100",
                    "DH7863-100"]

            resData = []

            for sku in skus:
                url = API + sku
                response = requests.get(url)
                resData.append(response.json()[
                    'results'][0]['estimatedMarketValue'])

                culture = 0
                culture += resData[0] * .125
                culture += resData[1] * .14
                culture += resData[2] * .150
                culture += resData[3] * .075
                culture += resData[4] * .011
                culture += resData[5] * .18
                culture += resData[6] * .08
                culture += resData[7] * .185
                culture += resData[8] * .017
                culture += resData[9] * .037

                db = cluster[DATABASE_NAME]
                stats = db[COLLECTION_NAME2]
                stats.insert_one({"price": culture})
                update.message.reply_text("Baseline Set!")

        except Exception as error:
            print('Cause {}'.format(error))
            update.message.reply_text("Not Authorized!")


def xci_price(update, context):
    sender = update.message.from_user.username
    if sender == "zmill28" or sender == "el_malchemist":
        try:
            skus = ["555088-063",
                    "DO9392-700",
                    "DD1391-400",
                    "GW3355",
                    "DC9533-800",
                    "BB550WT1",
                    "GX2487",
                    "GW1229",
                    "DH9792-100",
                    "DH7863-100"]

            resData = []

            for sku in skus:
                url = API + sku
                response = requests.get(url)
                resData.append(response.json()[
                    'results'][0]['estimatedMarketValue'])
                culture = 0
                culture += resData[0] * .125
                culture += resData[1] * .14
                culture += resData[2] * .150
                culture += resData[3] * .075
                culture += resData[4] * .011
                culture += resData[5] * .18
                culture += resData[6] * .08
                culture += resData[7] * .185
                culture += resData[8] * .017
                culture += resData[9] * .037

                update.message.reply_text(
                    "Xsauce Culture Index is ${}".format(round(culture, 2)))

                db = cluster[DATABASE_NAME]
                stats = db[COLLECTION_NAME2]
                stats.update_one({"price": {"$exists": True}},
                                 {"$set": {"price": culture}})
        except Exception as error:
            print('Cause {}'.format(error))
            update.message.reply_text("Not Authorized!")


def send2db(update, context):
    selection = update.poll_answer.option_ids[0]
    wager = None
    isShort = bool
    if selection == 7:
        wager = 3000
        isShort = True
    elif selection == 6:
        wager = 2000
        isShort = True
    elif selection == 5:
        wager = 1000
        isShort = True
    elif selection == 4:
        wager = 500
        isShort = True
    elif selection == 3:
        wager = 500
        isShort = False
    elif selection == 2:
        wager = 1000
        isShort = False
    elif selection == 1:
        wager = 2000
        isShort = False
    elif selection == 0:
        wager = 3000
        isShort = False

    try:
        username = update.poll_answer.user.username
        db = cluster[DATABASE_NAME]
        participants = db[COLLECTION_NAME1]
        stats = db[COLLECTION_NAME2]
        res = participants.find({"username": username})[0]
        res2 = stats.find()[0]
        currIndexPrice = res2['price']
        currFunds = res['funds']
        currSelect = res['selection']
        position = wager / currIndexPrice
        currSelect.append({"direction": isShort, "amount": wager})
        if isShort == False:
            participants.update_one({"username": username}, {"$set": {
                "position": {"Long": {"shares": position, "buyIn": currIndexPrice}, "Short": {"shares": res['position']['Short']['shares'], "buyIn": res['position']['Short']['buyIn']}}, "selection": [currSelect], "funds": currFunds - wager, "trades": res['trades'] + 1}})
        else:
            participants.update_one({"username": username}, {"$set": {
                "position": {"Short": {"shares": position, "buyIn": currIndexPrice}, "Long": {"shares": res['position']['Long']['shares'], "buyIn": res['position']['Long']['buyIn']}}, "selection": [currSelect], "funds": currFunds - wager, "trades": res['trades'] + 1}})
    except Exception as error:
        print('Cause {}'.format(error))


def play(update, context):
    sender = update.message.from_user.username
    try:
        db = cluster[DATABASE_NAME]
        participants = db[COLLECTION_NAME1]
        res = participants.find({"username": sender})
        if len(list(res.clone())) > 0:
            update.message.reply_text("Nice try! No such thing as free")
        else:
            participants.insert_one(
                {"username": sender, "funds": 10000, "position": {"Long": {"shares": 0, "buyIn": {"purchased": 0, "amount_spent": 0}}, "Short": {"shares": 0, "buyIn": {"purchased": 0, "amount_spent": 0}}}, "trades": {"total": 0, "tradeDetails": []}})
            update.message.reply_text(
                "Welcome {},\n This is v0 of Daily Bread. Your account has been funded with $10,000".format(sender))
    except Exception as error:
        print('Cause{}'.format(error))


def portfolio(update, context):
    username = update.message.from_user.username
    try:
        db = cluster[DATABASE_NAME]
        participants = db[COLLECTION_NAME1]
        stats = db[COLLECTION_NAME2]
        res2 = stats.find()[0]
        currIndexPrice = res2['price']
        res = participants.find({"username": username})[0]
        avg_buy_price_long = 0
        avg_buy_price_short = 0
        if res['position']['Long']['buyIn']['amount_spent'] > 0:
            avg_buy_price_long = res['position']['Long']['buyIn']['amount_spent'] / \
                res['position']['Long']['buyIn']['purchased']
        if res['position']['Short']['buyIn']['amount_spent'] > 0:
            avg_buy_price_short = res['position']['Short']['buyIn']['amount_spent'] / \
                res['position']['Short']['buyIn']['purchased']
        Long = res['position']["Long"]['shares'] * currIndexPrice + \
            (currIndexPrice - avg_buy_price_long) * \
            res['position']['Long']['shares']
        Short = res['position']["Short"]['shares'] * currIndexPrice + \
            (avg_buy_price_short - currIndexPrice) * \
            res['position']["Short"]['shares']
        pnl = round((res['funds'] + (Long + Short)) - 10000, 3)
        if math.isclose(pnl, 0.00):
            pnl = 0
        message = "*Balance:* ${}\n" \
            "*Holdings(of XCI)*: {} Short / {} Long\n" \
            "*Total(Unsettled)*: ${}\n" \
            "*Avg Buy Price*:{} Short / {} Long\n" \
            "*PNL*: ${}\n" \
            "*Total Trades*: {}"

        update.message.reply_text(
            message.format(round(res['funds'], 3),
                           round(res['position']['Short']['shares'], 3),
                           round(res['position']['Long']['shares'], 3),
                           round(Long + Short, 2),
                           round(avg_buy_price_short, 3),
                           round(avg_buy_price_long, 3),
                           pnl,
                           res['trades']['total']),
            parse_mode='Markdown'
        )

    except Exception as error:
        update.message.reply_text("You hold no positions/ Error")
        print('Cause {}'.format(error))


def instructions(update, context):
    update.message.reply_text("These will be the instructions {}".format(id))


def open(update, context):
    sender = update.message.from_user.username
    x = re.split("\s", update.message.text)
    wager = (x[2])
    try:
        wager = float(x[2])
    except ValueError as error:
        update.message.reply_text('Please enter a number')
    try:
        db = cluster[DATABASE_NAME]
        participants = db[COLLECTION_NAME1]
        stats = db[COLLECTION_NAME2]
        res = stats.find()[0]
        currIndexPrice = res['price']
        balance = participants.find({"username": sender})[0]
        funds = balance['funds']
        trades = balance['trades']['tradeDetails']
        if wager > funds:
            raise ValueError('More than you have in your account')
        purchased = wager / currIndexPrice

        if x[1] == "short":
            trades.append({"direction": x[1], "amount": wager})
            participants.update_one({"username": sender}, {"$set": {
                "position": {"Short": {"shares": balance['position']['Short']['shares'] + purchased, "buyIn": {"purchased": balance['position']['Short']
                                                                                                               ['buyIn']['purchased'] + purchased, "amount_spent": balance['position']['Short']
                                                                                                               ['buyIn']['amount_spent'] + wager}}, "Long": {"shares": balance['position']['Long']['shares'], "buyIn": {"purchased": balance['position']['Long']['buyIn']['purchased'], "amount_spent": balance['position']['Long']['buyIn']['amount_spent']}}}, "funds": funds - wager, "trades": {"total": balance['trades']['total'] + 1, "tradeDetails": trades}}})
            update.message.reply_text('Short position has been opened!')
        if x[1] == "long":
            trades.append({"direction": x[1], "amount": wager})
            participants.update_one({"username": sender}, {"$set": {
                "position": {"Short": {"shares": balance['position']['Short']['shares'], "buyIn": {"purchased": balance['position']['Short']['buyIn']['purchased'], "amount_spent": balance['position']['Short']['buyIn']['amount_spent']}}, "Long": {"shares": balance['position']['Long']['shares'] + purchased, "buyIn": {"purchased": balance['position']['Long']
                                                                                                                                                                                                                                                                                                                             ['buyIn']['purchased'] + purchased, "amount_spent": balance['position']['Long']
                                                                                                                                                                                                                                                                                                                             ['buyIn']['amount_spent'] + wager}}}, "funds": funds - wager, "trades": {"total": balance['trades']['total'] + 1, "tradeDetails": trades}}})
            update.message.reply_text('Long position has been opened!')

    except Exception and ValueError as error:
        print('Cause {}'.format(error))
        update.message.reply_text('{}'.format(error))


def close(update, context):
    sender = update.message.from_user.username
    x = re.split("\s", update.message.text)
    reduction = (x[2])
    try:
        if x[2] == "max":
            reduction = "max"
        else:
            reduction = float(x[2])
    except ValueError as error:
        return update.message.reply_text('Please enter a number')
    try:
        db = cluster[DATABASE_NAME]
        participants = db[COLLECTION_NAME1]
        stats = db[COLLECTION_NAME2]
        res = stats.find()[0]
        currIndexPrice = res['price']
        balance = participants.find({"username": sender})[0]
        funds = balance['funds']
        trades = balance['trades']['tradeDetails']

        if x[1] == "short":
            avg_buy_price = balance['position']['Short']['buyIn']['amount_spent'] / \
                balance['position']['Short']['buyIn']['purchased']
            if reduction == "max":
                reduction = balance['position']['Short']['shares'] - 1e-09
            wager = avg_buy_price * reduction
            cash_out = ((avg_buy_price - currIndexPrice) * reduction) + \
                (reduction * currIndexPrice)
            print(cash_out)
            if math.isclose(balance['position']['Short']['shares'], reduction) == False and reduction > balance['position']['Short']['shares']:
                raise ValueError('More than you have in your account')
            trades.append({"direction": x[1], "amount": reduction})
            participants.update_one({"username": sender}, {"$set": {
                "position": {"Short": {"shares": balance['position']['Short']['shares'] - reduction, "buyIn": {"purchased": balance['position']['Short']['buyIn']['purchased'] - reduction, "amount_spent": balance['position']['Short']['buyIn']['amount_spent'] - wager}}, "Long": {"shares": balance['position']['Long']['shares'], "buyIn": {"purchased": balance['position']['Long']['buyIn']['purchased'], "amount_spent": balance['position']['Long']['buyIn']['amount_spent']}}}, "funds": funds + cash_out, "trades": {"total": balance['trades']['total'] + 1, "tradeDetails": trades}}})
            update.message.reply_text('Short position has been closed!')
        if x[1] == "long":
            avg_buy_price = balance['position']['Long']['buyIn']['amount_spent'] / \
                balance['position']['Long']['buyIn']['purchased']
            if reduction == "max":
                reduction = balance['position']['Long']['shares'] - 1e-09
            wager = avg_buy_price * reduction
            cash_out = ((currIndexPrice - avg_buy_price) * reduction) + \
                (reduction * currIndexPrice)
            if math.isclose(balance['position']['Long']['shares'], reduction) == False and reduction > balance['position']['Long']['shares']:
                raise ValueError('More than you have in your account')
            trades.append({"direction": x[1], "amount": reduction})
            participants.update_one({"username": sender}, {"$set": {
                "position": {"Short": {"shares": balance['position']['Short']['shares'], "buyIn": {"purchased": balance['position']['Short']['buyIn']['purchased'], "amount_spent": balance['position']['Short']['buyIn']['amount_spent']}}, "Long": {"shares": balance['position']['Long']['shares'] - reduction, "buyIn": {"purchased": balance['position']['Long']['buyIn']['purchased'] - reduction, "amount_spent": balance['position']['Long']['buyIn']['amount_spent'] - wager}}}, "funds": funds + cash_out, "trades": {"total": balance['trades']['total'] + 1, "tradeDetails": trades}}})
            update.message.reply_text('Long position has been closed!')

    except Exception and ValueError as error:
        print('Cause {}'.format(error))
        update.message.reply_text('{}'.format(error))


def help(update, context):
    update.message.reply_text(
        """
  /play -> Welcome to the channel! Use this command to get $10,000 dollars to start up!
  /close
  /portfolio -> Show your current index holdings
  /help -> Shows this message
  /instructions -> See how to play daily bread
  /website -> Learn about Xsauce and cultural assets
  """
    )


def poll(update, context):
    sender = update.message.from_user.username
    if sender == "zmill28" or sender == "el_malchemist":
        db = cluster[DATABASE_NAME]
        stats = db[COLLECTION_NAME2]
        res = stats.find()[0]
        currPrice = res['price']
        base_url = CHAT
        parameters = {
            "chat_id": "-1001872658552",
            "question": "How much are you wagering on the Culture Index? - Current Price:{}".format(round(currPrice, 2)),
            "options": json.dumps(["$3,000(Long)", "$2,000(Long)", "$1,000(Long)", "$500(Long)", "$500(Short)", "$1000(Short)", "$2000(Short)", "$3000(Short)"]),
            "is_anonymous": False,
        }
        resp = requests.get(base_url, data=parameters)
    else:
        update.message.reply_text('Not Authorized')


def website(update, context):
    update.message.reply_text(
        "Check out our website to see what Xsauce is all about: https://xsauce.io/ ")


main()
