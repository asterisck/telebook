import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import requests
from bs4 import BeautifulSoup

def fetch_books_info(query):
    url = 'https://www.libgen.is/search.php?req=' + query + '&open=0&res=25&view=simple&phrase=1&column=def'
    response = requests.get(url)
    
    autho = []
    titl = []
    yea = []
    lan = []
    lin = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        tx_elements = soup.find_all('tr', {'bgcolor': '', 'valign': 'top'})
        ty_elements = soup.find_all('tr', {'bgcolor': '#C6DEFF', 'valign': 'top'})
        tr_elements = result = [item for pair in zip(ty_elements,tx_elements) for item in pair]

        for tr_element in tr_elements:
            td_elements = tr_element.find_all('td')

            author = td_elements[1].text.strip()
            autho.append(author)
            title = td_elements[2].text.strip()
            titl.append(title)
            year = td_elements[4].text.strip()
            yea.append(year)
            lang = td_elements[6].text.strip()
            lan.append(lang)
            link = td_elements[9].a['href']
            lin.append(link)

        return {
            'authors': autho,
            'titles': titl,
            'years': yea,
            'languages': lan,
            'links': lin
        }
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def pdfLink(link):
    a=requests.get(link)
    b=a.text
    start=b.find('https://cloudflare')
    end=b.find('\">Cl',start)
    start1=b.find('https://gateway.ipfs')
    end1=b.find('\">IP',start1)
    return [b[start:end],b[start1:end1]]

def book_handler(update, context):
    message = update.message.text
    if message.startswith('/book '):
        book_name = message[6:]
        reply_text = f'Hello, {book_name}!'
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)



def book_handler(update, context):
    message = update.message.text
    if message.startswith('/book '):
        book_name = message[6:]
        result = fetch_books_info(book_name)
        if len(result['links']):
            link=result['links'][0]
            link=pdfLink(link)
            print(link)
            reply_text = f'Your book, {book_name}!\n\nLink1 : {link[0]}\n\nLink2 : {link[1]}'
        else:
            reply_text = "No book found. Check spelling of your query"
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)

bot = telegram.Bot(token='6896534467:AAH_8RPJLJdl822-SoxlBMF4oGRAcyyzYM0')
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, book_handler))
updater.start_polling()
