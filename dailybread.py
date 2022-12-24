import math
from telegram import *
from telegram.ext import *
import requests
import re
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import pymongo
from pymongo import MongoClient
from models import *
import processes.play
import processes.info
import processes.portfolio
import processes.open
import processes.close
import processes.manage_index
import processes.composition
load_dotenv()


PASSWORD = os.environ['password']
USERNAME = os.environ['username']
BOT_TOKEN = os.environ['bot_token']
API = os.environ['api']
CHAT = os.environ['chat']
DATABASE_NAME = os.environ['db_name']
COLLECTION_NAME1 = os.environ['collection_name1']
COLLECTION_NAME2 = os.environ['collection_name2']
URL = os.environ['db_url']
cluster = MongoClient(URL)


def price_update(context):
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
            sneak_url = API + sku
            response = requests.get(sneak_url)
            print(response.json()[
                'results'][0]['estimatedMarketValue'])
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
        context.bot.send_message(CHAT,
                                 text="Xsauce Culture Index is ${}".format(round(culture, 2)))

        processes.manage_index.add_index_statistics("xci" , "Xsauce Culture Index" ,culture)

    except Exception as error:
        print('Cause {}'.format(error))

def price_update2(context):
    try:
        culture = 150.77
        context.bot.send_message(CHAT,
                                 text="New Index is ${}".format(round(culture, 2)))

        processes.manage_index.add_index_statistics("nix" , "New Index" ,culture)
    except Exception as error:
        print('Cause {}'.format(error))

def price_update3(context):
    try:
        culture = 335.20
        context.bot.send_message(CHAT,
                                 text="Sneaker S&P 50 is ${} *temp".format(round(culture, 2)))

        processes.manage_index.add_index_statistics("S&P50" , "Sneaker S&P 50 (S&P50)" ,culture)
    except Exception as error:
        print('Cause {}'.format(error))

def index_price(update, context):
    message = update.message.text
    try:
        index_info = processes.info.get_index_latest_info(message)
        update.message.reply_text("{} is ${}. Updated on {} at {} UTC".format(
            index_info.full_name, index_info.price, index_info.date, index_info.time))
    except Exception as error:
        print('Cause {}'.format(error))
        update.message.reply_text('{}'.format(error))

def index_composition(update, context):
    message = update.message.text
    try:
        composition_string = processes.composition.get_index_composition(message)
        update.message.reply_text(composition_string, parse_mode='Markdown')
    except Exception as error:
        print('Cause {}'.format(error))
        update.message.reply_text('{}'.format(error))


def play(update, context):
    sender = update.message.from_user.username
    try:
        reply = processes.play.play(sender)
        update.message.reply_text(reply)
    except Exception as error:
        print('Cause{}'.format(error))


def welcome(update, context):
    new_members = update.effective_message.new_chat_members

    context.bot.send_message(CHAT,
                             text="Welcome to the Xchange {}!\n\nUse the /help command to see all options".format(new_members[-1].username))


def portfolio(update, context):
    sender = update.message.from_user.username
    message = update.message.text
    try:
        portfolio = processes.portfolio.portfolio(sender, message)
        if type(portfolio) == Portfolio:
            formatted_message = format_portfolio_string(portfolio)

        elif type(portfolio) == TotalPortfolio:
            formatted_message = format_total_string(portfolio)
        update.message.reply_text(
                formatted_message,
                parse_mode='Markdown'
            )

    except Exception as error:
        update.message.reply_text("You hold no positions/ Error")
        print('Cause {}'.format(error))


def format_portfolio_string(portfolio: Portfolio):
    message = "*Index:* {}\n" \
        "*Balance:* ${}\n" \
        "*Holdings(of XCI)*: {} Short / {} Long\n" \
        "*Total(Unsettled)*: ${}\n" \
        "*Avg Buy Price*:{} Short / {} Long\n" \
        "*PNL*: ${}\n" \
        "*Total Trades*: {}"
    formatted_message = message.format(portfolio.index_name,
                            round(portfolio.funds, 3),
                           round(portfolio.short_shares, 3),
                           round(portfolio.long_shares, 3),
                           round(portfolio.long + portfolio.short, 2),
                           round(portfolio.avg_buy_price_short, 3),
                           round(portfolio.avg_buy_price_long, 3),
                           portfolio.pnl,
                           portfolio.number_of_trades)
    return formatted_message

def format_total_string(portfolio: Portfolio):
    message = "*Balance:* ${}\n" \
        "*Total(Unsettled)*: ${}\n" \
        "*PNL*: ${}\n" \
        "*Total Trades*: {}"
    formatted_message = message.format(
                           round(portfolio.funds, 3),
                           round(portfolio.long + portfolio.short, 2),
                           portfolio.pnl,
                           portfolio.number_of_trades)
    return formatted_message

def instructions(update, context):
    update.message.reply_text(
        "https://docs.xsauce.io/applications/how-it-works")


def open(update, context):
    sender = update.message.from_user.username
    message = update.message.text

    try:
        result = processes.open.open(sender, message)
        update.message.reply_text(result)
    except Exception and ValueError as error:
        print('Cause {}'.format(error))
        update.message.reply_text('{}'.format(error))


def close(update, context):
    sender = update.message.from_user.username
    message = update.message.text
    try:
        reply = processes.close.close(sender, message)
        update.message.reply_text(reply)
    except Exception and ValueError as error:
        print('Cause {}'.format(error))
        update.message.reply_text('{}'.format(error))

def list_index(update, context):
    ##warning the list is hard coded for now
    try:
        update.message.reply_text( "*Xsauce Index:* xci\n" \
        "*New Index:* nix\n" \
        "*Idiss Index*: ids\n", parse_mode='Markdown')
    except Exception and ValueError as error:
        print('Cause {}'.format(error))
        update.message.reply_text('{}'.format(error))


def help(update, context):
    update.message.reply_text(
        "/instructions -> Learn how to use the Xchange\n"
        "/play -> Use this command to get $10,000 dollars to start up!\n"
        "/list -> Show the list of available indexes\n"
        "/open -> Open a position\n"
        "/close -> Close a position\n"
        "/info -> Show the current price an index\n"
        "/portfolio -> Show your current portfolio holdings\n"
        "/portfolio [index_name]-> Show your current index holdings\n"
        "/help -> Shows this message\n"
        "/website -> Learn about Xsauce and cultural assets"
    )

def website(update, context):
    update.message.reply_text(
        "Check out our website to see what Xsauce is all about: https://xsauce.io/ ")


def main():
    updater = Updater(
        BOT_TOKEN, use_context=True)
    job_queue = updater.job_queue
    job_seconds = job_queue.run_repeating(
        price_update, interval=86400, first=1)
    job_seconds_2 = job_queue.run_repeating(
        price_update2, interval=86400, first=1)
    job_seconds_2 = job_queue.run_repeating(
        price_update3, interval=86400, first=1)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('close', close))
    dispatcher.add_handler(CommandHandler('portfolio', portfolio))
    dispatcher.add_handler(CommandHandler('play', play))
    dispatcher.add_handler(CommandHandler('list', list_index))
    dispatcher.add_handler(CommandHandler('website', website))
    dispatcher.add_handler(CommandHandler('open', open))
    dispatcher.add_handler(CommandHandler('info', index_price))
    dispatcher.add_handler(CommandHandler('comp', index_composition))
    dispatcher.add_handler(CommandHandler('instructions', instructions))
    dispatcher.add_handler(MessageHandler(
        Filters.status_update.new_chat_members, welcome))

    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()


main()
